import os
import subprocess
import importlib

def optimize_meets(seats, hanchan_count):
    table_count = len(seats[0])
    N = table_count * 4
    indirect_meetup_min = int(N ** 0.5)

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
    k penalty levels / 1*{indirect_meetup_min} /
    p players / 1*{N} /;

Alias (p, p1, p2, p3);
Alias (h, h1, h2);
Alias (t, t1, t2);

Parameters
    seats(h,t,p) original seating arrangement
    penalty_threshold(k) threshold for each penalty level
    penalty_coefficient(k) coefficient for each penalty level;
    
$loaddc seats
$gdxin

Scalar hanchan_count / {hanchan_count} /;
Scalar indirect_meetup_min / {indirect_meetup_min} /;

penalty_threshold(k) = indirect_meetup_min - ord(k) + 1;
penalty_coefficient(k) = 1000 * (indirect_meetup_min - ord(k) + 1);

Binary Variables 
    x(h) 'binary variable for selecting hanchan'
    meets(p1,p2,h) 'binary variable indicating if p1 and p2 meet in hanchan h'
    meets_any(p1,p2) 'binary variable indicating if p1 and p2 meet in any selected hanchan'
    penalty_level(p1,p2,k) 'binary variable for each penalty level'
    indirect_meet(p1,p2,p3) 'binary variable indicating if p1 and p2 meet indirectly through p3';
Variables
    z 'objective function value'
    indirect_meetups(p1,p2) 'indirect meetups for each pair of players'
    penalty(p1,p2) 'penalty for each pair of players';

Positive Variable indirect_meetups;
Positive Variable penalty;

Equations
    obj 'define objective function'
    select_hanchan 'select exactly hanchan_count hanchan'
    define_meets(p1,p2,h) 'define the meets variable'
    define_meets_any(p1,p2) 'define the meets_any variable'
    define_indirect_meet1(p1,p2,p3) 'define the indirect_meet variable (condition 1)'
    define_indirect_meet2(p1,p2,p3) 'define the indirect_meet variable (condition 2)'
    define_indirect_meet3(p1,p2,p3) 'define the indirect_meet variable (condition 3)'
    count_indirect_meetups(p1,p2) 'count indirect meetups for each pair of players'
    calculate_penalty(p1,p2) 'calculate penalty for each pair of players'
    define_penalty_level(p1,p2,k) 'define penalty level for each pair and level'
    ensure_one_penalty_level(p1,p2) 'ensure only one penalty level is active';

obj.. z =e= sum((p1,p2)$(ord(p1) < ord(p2)), penalty(p1,p2));

select_hanchan.. sum(h, x(h)) =e= hanchan_count;

define_meets(p1,p2,h)$(ord(p1) < ord(p2)).. 
    meets(p1,p2,h) =e= sum(t, seats(h,t,p1) * seats(h,t,p2)) * x(h);

define_meets_any(p1,p2)$(ord(p1) < ord(p2))..
    meets_any(p1,p2) =e= sum(h, meets(p1,p2,h));

define_indirect_meet1(p1,p2,p3)$(ord(p1) < ord(p2) and ord(p3) <> ord(p1) and ord(p3) <> ord(p2))..
    indirect_meet(p1,p2,p3) =l= meets_any(p1,p3);

define_indirect_meet2(p1,p2,p3)$(ord(p1) < ord(p2) and ord(p3) <> ord(p1) and ord(p3) <> ord(p2))..
    indirect_meet(p1,p2,p3) =l= meets_any(p2,p3);

define_indirect_meet3(p1,p2,p3)$(ord(p1) < ord(p2) and ord(p3) <> ord(p1) and ord(p3) <> ord(p2))..
    indirect_meet(p1,p2,p3) =g= meets_any(p1,p3) + meets_any(p2,p3) - 1;

count_indirect_meetups(p1,p2)$(ord(p1) < ord(p2)).. 
    indirect_meetups(p1,p2) =e= sum(p3$(ord(p3) <> ord(p1) and ord(p3) <> ord(p2)), indirect_meet(p1,p2,p3));

calculate_penalty(p1,p2)$(ord(p1) < ord(p2))..
    penalty(p1,p2) =e= sum(k, penalty_coefficient(k) * penalty_level(p1,p2,k));

define_penalty_level(p1,p2,k)$(ord(p1) < ord(p2))..
    penalty_level(p1,p2,k) =l= 1 - (indirect_meetups(p1,p2) - penalty_threshold(k)) / (indirect_meetup_min + 1);

ensure_one_penalty_level(p1,p2)$(ord(p1) < ord(p2))..
    sum(k, penalty_level(p1,p2,k)) =e= 1;

Model seating /all/;

Option reslim = 300;
Option threads = 1;
Option solvelink = 5;

Option sysout = on;
seating.optfile = 1;
$onecho > cplex.opt
iis yes
$offecho

Solve seating using mip minimizing z;

file results / 'results_{N}.txt' /;
file debug / 'indirect_{N}.txt' /;

put results;
if(seating.modelstat = 4,
    put "Model status: Infeasible" /;
    put "IIS information in the LST file" /;
else
    put 'Selected hanchan:'/;
    loop(h$(x.l(h) > 0.5),
        put h.tl /;
    );
);
put 'done' /;
putclose;

put debug;
put 'Total penalty: ' z.l:0:0 /;
loop((p1,p2)$(ord(p1) < ord(p2)),
    put p1.tl:0 ',' p2.tl:0 ',' 
    indirect_meetups.l(p1,p2):0:0 ',' 
    penalty.l(p1,p2):0:0 /;
);
putclose;
""")

    # Run GAMS optimization
    result = subprocess.run(["gams", gams_file], capture_output=False, text=True)

    # Load and return results
    if not os.path.exists(f"results_{N}.txt"):
        print(f"Error: Results file results_{N}.txt was not created.")
        print("GAMS output:")
        print(result.stdout)
        print(result.stderr)
        return None

    with open(f"results_{N}.txt", "r") as f:
        content = f.read()

    print("GAMS output:")
    print(content)
    if "Model status: Infeasible" in content:
        print("The problem is infeasible. Check the LST file for IIS information.")
        return None
    
    # Read results
    selected_hanchan = []
    for line in content.split('\n'):
        if line.startswith("Selected hanchan:"):
            continue
        elif line.strip() == "done":
            break
        else:
            selected_hanchan.append(int(line))

    # Create new_seats based on selected hanchan
    new_seats = [seats[h-1] for h in selected_hanchan]

    # Write new seats to Python file
    with open(f"meetups/{N}x{hanchan_count}.py", "w") as f:
        out = f"{new_seats}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")

    # Clean up temporary files
    for file in [gams_file, f"seats_{N}.gms", f"seats_{N}.gdx", f"seats_{N}.lst",
                f"optimize_{N}.lst", f"results_{N}.txt"]:
        if os.path.exists(file):
            os.remove(file)

    return new_seats

if __name__ == "__main__":
    tst = importlib.import_module("sgp.60").seats
    seats = optimize_meets(tst, 6)
    from stats import make_stats
    out = make_stats(seats)
    out = out[out.find("Indirect Meetup frequencies:"):]
    print(f"optimised: {out}\n\n")
    out1 = make_stats(tst[0:6])
    out1 = out1[out1.find("Indirect Meetup frequencies:"):]
    print(f"baseline: {out1}")
