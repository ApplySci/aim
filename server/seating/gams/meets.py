import os
import subprocess
import importlib
import sys

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
    print("GDX creation output:", result.stdout)
    print("GDX creation errors:", result.stderr)

    if not os.path.exists(gdx_file):
        print(f"Error: GDX file {gdx_file} was not created.")
        return None
    print("End of GDX creation")

    # Create optimize_{N}.gms file
    gams_file = f"optimize_{N}.gms"
    with open(gams_file, "w") as f:
        f.write(f"""
$set gdxincurdir 1
$gdxin {gdx_file}
$if not exist {gdx_file} $abort 'GDX file does not exist'

Sets
    h hanchan / 1*{len(seats)} /
    t tables / 1*{table_count} /
    p players / 1*{N} /
    s selected hanchan / 1*{hanchan_count} /;

Alias (p, p1, p2);
Alias (h, h1, h2);
Alias (t, t1, t2);

Parameter seats(h,t,p) original seating arrangement;

$loaddc seats
$gdxin

display seats;
display h, t, p;

Parameter indirect_meetup_min / {indirect_meetup_min} /;

Variables
    x(s,h) binary variable for selecting hanchan
    y(s,h1,h2,p1,p2) linearization variable
    z total indirect meetups;

Binary Variable x;
Binary Variable y;

Equations
    obj define objective function
    select_hanchan(s) select exactly {hanchan_count} hanchan
    no_duplicate_tables(t,p,s) no duplicate tables in selected hanchan
    indirect_meetups calculate total indirect meetups
    linearization1(s,h1,h2,p1,p2) linearization constraint 1
    linearization2(s,h1,h2,p1,p2) linearization constraint 2
    linearization3(s,h1,h2,p1,p2) linearization constraint 3;

obj.. z =e= sum((s,h1,t1,p1,p2,h2,t2)$(ord(p1) < ord(p2) and ord(h1) ne ord(h2)), y(s,h1,h2,p1,p2) * seats(h1,t1,p1) * seats(h2,t2,p2));

select_hanchan(s).. sum(h, x(s,h)) =e= 1;

no_duplicate_tables(t,p,s).. sum(h, x(s,h) * seats(h,t,p)) =l= 1;

indirect_meetups.. z =g= indirect_meetup_min;

linearization1(s,h1,h2,p1,p2)$(ord(p1) < ord(p2) and ord(h1) ne ord(h2)).. y(s,h1,h2,p1,p2) =l= x(s,h1);
linearization2(s,h1,h2,p1,p2)$(ord(p1) < ord(p2) and ord(h1) ne ord(h2)).. y(s,h1,h2,p1,p2) =l= x(s,h2);
linearization3(s,h1,h2,p1,p2)$(ord(p1) < ord(p2) and ord(h1) ne ord(h2)).. y(s,h1,h2,p1,p2) =g= x(s,h1) + x(s,h2) - 1;

Model seating /all/;

Option optcr = 0.05;
Option reslim = 300;

Solve seating using mip maximizing z;

execute_unload "results_{N}.gdx" x.l, y.l, z.l;
""")

    # Run GAMS optimization
    result = subprocess.run(["gams", gams_file], capture_output=False, text=True)

    # Load and return results
    if os.path.exists(f"results_{N}.gdx"):
        result = subprocess.run(["gdxdump", f"results_{N}.gdx"], capture_output=True, text=True)
        print("Results GDX file contents:")
        print(result.stdout)
        # Here you would parse the results and return them in a suitable format
        return "Results parsed from GDX file"
    else:
        print(f"Error: Results file results_{N}.gdx was not created.")
        return None

if __name__ == "__main__":
    tst = importlib.import_module("sgp.40").seats
    optimize_meets(tst, 6)