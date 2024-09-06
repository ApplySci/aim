import os
import subprocess
import importlib
import sys

def optimize_meets(seats, hanchan_count):
    table_count = len(seats[0])
    N = table_count * 4
    indirect_meetup_min = int(N ** 0.5)
    print(f"N: {N}, indirect_meetup_min: {indirect_meetup_min}")

    # Write seats data to GDX
    gdx_file = f"seats_{N}.gdx"
    with open(f"seats_{N}.gms", "w") as f:
        f.write(f"""
Set
    h hanchan / 1*{len(seats)} /
    t tables / 1*{table_count} /
    p players / 1*{N} /;

Parameter seats(h,t,p) /
""")
        for h, hanchan in enumerate(seats, 1):
            for t, table in enumerate(hanchan, 1):
                for i, p in enumerate(table, 1):
                    f.write(f"{h}.{t}.{p} 1\n")
        f.write("/;\n")
        f.write(f"execute_unload '{gdx_file}', seats;")

    # Run GAMS to create GDX
    result = subprocess.run(["gams", f"seats_{N}.gms"], capture_output=True, text=True)

    if not os.path.exists(gdx_file):
        print(f"Error: GDX file {gdx_file} was not created.")
        print("GAMS output:", result.stdout)
        print("GAMS error:", result.stderr)
        return None

    # Create optimize_{N}.gms file
    gams_file = f"optimize_{N}.gms"
    with open(gams_file, "w") as f:
        f.write(f"""
$set gdxincurdir 1
$gdxin {gdx_file}
$if not exist {gdx_file} $abort 'GDX file does not exist'

$offsymxref offsymlist
Option limrow = 0, limcol = 0;
Option solprint = off;

Sets
    h hanchan / 1*{len(seats)} /
    t tables / 1*{table_count} /
    p players / 1*{N} /;

Alias (p, p1, p2);
Alias (h, h1, h2);
Alias (t, t1, t2);

Parameter seats(h,t,p) original seating arrangement;

$loaddc seats
$gdxin

Scalar hanchan_count / {hanchan_count} /;
Scalar indirect_meetup_min / {indirect_meetup_min} /;

Binary Variables 
    x(h) 'binary variable for selecting hanchan'
    y(h1,h2) 'binary variable for selecting pair of hanchan';
Variables
    z 'total indirect meetups'
    slack 'slack variable for indirect meetups constraint';

Positive Variable slack;

Equations
    obj 'define objective function'
    select_hanchan 'select exactly {hanchan_count} hanchan'
    indirect_meetups 'calculate total indirect meetups'
    linearize1(h1,h2) 'linearization constraint 1'
    linearize2(h1,h2) 'linearization constraint 2'
    linearize3(h1,h2) 'linearization constraint 3';

obj.. z =e= sum((h1,h2,t1,t2,p1,p2)$(ord(p1) < ord(p2) and ord(h1) < ord(h2)), 
                y(h1,h2) * seats(h1,t1,p1) * seats(h2,t2,p2)) - 1000000 * slack;

select_hanchan.. sum(h, x(h)) =e= hanchan_count;

indirect_meetups.. z + slack =g= indirect_meetup_min;

linearize1(h1,h2)$(ord(h1) < ord(h2)).. y(h1,h2) =l= x(h1);
linearize2(h1,h2)$(ord(h1) < ord(h2)).. y(h1,h2) =l= x(h2);
linearize3(h1,h2)$(ord(h1) < ord(h2)).. y(h1,h2) =g= x(h1) + x(h2) - 1;

Model seating /all/;

Option reslim = 300;
Option threads = 1;
Option solvelink = 5;

Option sysout = on;
seating.optfile = 1;
$onecho > cplex.opt
iis yes
$offecho

Solve seating using mip maximizing z;

file results / 'results_{N}.txt' /;
put results;

if(seating.modelstat = 4,
    put "Model status: Infeasible" /;
    put "IIS information in the LST file" /;
else
    put 'Selected hanchan:'/;
    loop(h$(x.l(h) > 0.5),
        put h.tl /;
    );
    put 'Objective value: ' z.l:10:2 /;
    put 'Slack value: ' slack.l:10:8 /;
);

put 'done' /;
putclose;
""")

    # Run GAMS optimization
    result = subprocess.run(["gams", gams_file], capture_output=False, text=True)

    # Check GAMS output
    if result.returncode != 0:
        print("GAMS error:")
        print(result.stdout)
        print(result.stderr)
        return None

    # Load and return results
    results_file = f"results_{N}.txt"
    if not os.path.exists(results_file):
        print(f"Error: Results file results_{N}.txt was not created.")
        print("GAMS output:")
        print(result.stdout)
        print(result.stderr)
        return None

    with open(results_file, "r") as f:
        content = f.read()
        if "Model status: Infeasible" in content:
            print("The problem is infeasible. Check the LST file for IIS information.")
            return None
            
    selected_hanchan = []
    for line in content.split('\n'):
        if line.startswith("Selected hanchan:"):
            continue
        if line.startswith("Objective value:") or line.startswith("Slack value:") or line.strip() == "done":
            break
        selected_hanchan.append(int(line))

    # Create new_seats based on selected hanchan
    new_seats = [seats[h-1] for h in selected_hanchan]

    # Write new seats to Python file
    with open(f"meetups/{N}x{hanchan_count}.py", "w") as f:
        out = f"{new_seats}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")

    # Clean up temporary files
    for file in [gams_file, f"seats_{N}.gms", f"seats_{N}.gdx",f"seats_{N}.lst",
                 f"optimize_{N}.lst", f"results_{N}.txt"]:
        if os.path.exists(file):
            os.remove(file)
    new_seats = [seats[h-1] for h in selected_hanchan]

    print(content)
    return new_seats

if __name__ == "__main__":
    tst = importlib.import_module("sgp.40").seats
    seats = optimize_meets(tst, 6)
    from stats import make_stats
    out = make_stats(seats)
    print(out)
