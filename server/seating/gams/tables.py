import os
import subprocess


def optimize_seating(seats, hanchan_count):
    # Calculate table_max
    table_count = len(seats[0])
    table_max = (hanchan_count + table_count - 1) // table_count
    N = table_count * 4
    # Write GAMS file
    gams_file = f"optimize_{N}.gms"
    with open(gams_file, "w") as f:
        f.write(f"""
Sets
    h hanchan / 1*{len(seats)} /
    t tables / 1*{table_count} /
    p players / 1*{N} /
    s selected hanchan / 1*{hanchan_count} /;

Alias (t, t1);
Alias (h, h1);

Parameter 
    seats(h,t,p) original seating arrangement
    table_max / {table_max} /;

$gdxin seats_{N}.gdx
$load seats
$gdxin

Variables
    z objective value;

Positive Variables
    excess(p,t) excess appearances for each player at each table;

Binary Variables
    y(h) whether hanchan h is selected
    w(s,h) whether selected hanchan s comes from original hanchan h
    v(s,h,t,t1) whether table t in selected hanchan s comes from table t1 in original hanchan h;

Equations
    obj objective function
    select_hanchan select exactly hanchan_count hanchan
    one_source_per_selected(s) each selected hanchan comes from one original hanchan
    maintain_order(s) maintain order of selected hanchan
    one_table_per_original(s,h,t) select one table from each original hanchan
    one_destination_per_table(s,h,t) each original table goes to one destination
    link_w_and_v(s,h) link w and v variables
    define_excess(p,t) define excess appearances
    unique_selection(h) ensure each hanchan is selected at most once;

obj.. z =e= sum((p,t), excess(p,t));

select_hanchan.. sum(h, y(h)) =e= card(s);

one_source_per_selected(s).. sum(h, w(s,h)) =e= 1;

maintain_order(s)$(ord(s) < card(s)).. 
    sum(h, ord(h) * w(s,h)) =l= sum(h, ord(h) * w(s+1,h));

one_table_per_original(s,h,t).. sum(t1, v(s,h,t,t1)) =e= w(s,h);

one_destination_per_table(s,h,t).. sum(t1, v(s,h,t1,t)) =l= 1;

link_w_and_v(s,h).. w(s,h) =e= sum((t,t1), v(s,h,t,t1)) / card(t);

define_excess(p,t).. excess(p,t) =g= sum((s,h,t1), seats(h,t1,p) * v(s,h,t,t1)) - table_max;

unique_selection(h).. sum(s, w(s,h)) =l= 1;

Model seating /all/;

Option optcr = 0.0;
Option threads = 4;

Solve seating using mip minimizing z;

file results / 'results_{N}.txt' /;
put results;
loop((s,h,t,t1)$(v.l(s,h,t,t1) > 0.5),
    loop(p$(seats(h,t1,p)),
        put s.tl, t.tl, p.tl /;
    );
);
putclose;
""")

    # Write seats data to GDX
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
                for p in table:
                    f.write(f"{h}.{t}.{p} 1\n")
        f.write("/;\n")
        f.write(f"execute_unload 'seats_{N}.gdx', seats;")

    # Run GAMS to create GDX
    subprocess.run(["gams", f"seats_{N}.gms"])

    # Run GAMS optimization
    try:
        process = subprocess.Popen(
            ["gams", gams_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            )
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
    except KeyboardInterrupt:
        print("GAMS optimization interrupted. Continuing with the rest of the script...")
    except Exception as e:
        print(f"An error occurred during GAMS optimization: {e}")

    # Check if results file exists
    if not os.path.exists(f"results_{N}.txt"):
        print("No results file found. GAMS optimization may have been interrupted or failed.")
        return None

    # Read results
    new_seats = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    with open(f"results_{N}.txt", "r") as f:
        for line in f:
            s, t, p = map(int, line.split())
            new_seats[s-1][t-1].append(p)

    # Write new seats to Python file
    with open(f"seats/{N}x{hanchan_count}.py", "w") as f:
        f.write(f"seats = {new_seats}\n")

    # Clean up temporary files
    for file in [gams_file, f"seats_{N}.gms", f"seats_{N}.gdx", f"results_{N}.txt"]:
        if os.path.exists(file):
            os.remove(file)

    return new_seats
