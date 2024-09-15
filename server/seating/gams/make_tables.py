import os
import subprocess
import importlib


def optimize_tables(seats):
    # Calculate table_max
    table_count = len(seats[0])
    hanchan_count = len(seats)
    table_max = (table_count + hanchan_count - 1) // table_count
    N = table_count * 4

    # Write GAMS file
    gams_file = f"optimize_{N}.gms"
    with open(gams_file, "w") as f:
        f.write(f"""
Sets
    h hanchan / 1*{hanchan_count} /
    t tables / 1*{table_count} /
    p players / 1*{N} /;

Alias (t, t1);

Parameter 
    seats(h,t,p) original seating arrangement
    table_max / {table_max} /;

$gdxin seats_{N}.gdx
$load seats
$gdxin

Variables
    z objective value
    penalty_2 penalty for visits 2 or more above table_max
    penalty_3 penalty for visits 3 or more above table_max;

Positive Variables
    excess(p,t) excess appearances for each player at each table
    excess_2(p,t) excess appearances 2 or more above table_max
    excess_3(p,t) excess appearances 3 or more above table_max;

Binary Variables
    v(h,t,t1) whether table t in hanchan h comes from table t1;

Equations
    obj objective function
    one_table_per_original(h,t) select one table from each original hanchan
    one_destination_per_table(h,t) each original table goes to one destination
    define_excess(p,t) define excess appearances
    define_excess_2(p,t) define excess appearances 2 or more above table_max
    define_excess_3(p,t) define excess appearances 3 or more above table_max
    calc_penalty_2 calculate penalty for excess 2
    calc_penalty_3 calculate penalty for excess 3
    fix_first_hanchan(t) fix the order of tables in the first hanchan;

obj.. z =e= sum((p,t), excess(p,t)) + 10 * penalty_2 + 100 * penalty_3;

one_table_per_original(h,t).. sum(t1, v(h,t,t1)) =e= 1;

one_destination_per_table(h,t).. sum(t1, v(h,t1,t)) =e= 1;

define_excess(p,t).. excess(p,t) =g= sum((h,t1), seats(h,t1,p) * v(h,t,t1)) - table_max;

define_excess_2(p,t).. excess_2(p,t) =g= sum((h,t1), seats(h,t1,p) * v(h,t,t1)) - (table_max + 1);

define_excess_3(p,t).. excess_3(p,t) =g= sum((h,t1), seats(h,t1,p) * v(h,t,t1)) - (table_max + 2);

calc_penalty_2.. penalty_2 =e= sum((p,t), excess_2(p,t));

calc_penalty_3.. penalty_3 =e= sum((p,t), excess_3(p,t));

fix_first_hanchan(t).. v('1',t,t) =e= 1;

Model seating /all/;

Option optcr = 0.0;
Option threads = 1;
Option solvelink = 5;
Option resLim = 600;

Solve seating using mip minimizing z;

file results / 'results_{N}.txt' /;
put results;
loop((h,t,t1)$(v.l(h,t,t1) > 0.5),
    loop(p$(seats(h,t1,p)),
        put h.tl, t.tl, p.tl /;
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
    with open(f"tables/{N}x{hanchan_count}.py", "w") as f:
        out = f"{new_seats}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")

    # Clean up temporary files
    for file in [gams_file, f"seats_{N}.gms", f"seats_{N}.gdx", f"results_{N}.txt",
                 f"optimize_{N}.lst", f"seats_{N}.lst"]:
        if os.path.exists(file):
            os.remove(file)

    return new_seats


if __name__ == "__main__":
    from stats import make_stats
    tst = importlib.import_module("meetups.60x8").seats
    seats = optimize_tables(tst)
    out1 = make_stats(tst)
    out1 = out1[
        out1.find("Table Visit frequencies:")
        :out1.find("Wind frequencies:")]
    print(f"baseline: {out1}")
    out = make_stats(seats)
    out = out[out.find("Table Visit frequencies:")
        :out.find("Wind frequencies:")]
    print(f"optimised: {out}\n\n")
