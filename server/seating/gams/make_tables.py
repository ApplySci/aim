"""
Table Optimization for Seating Arrangements

This module provides functionality to optimize table assignments for a given
seating arrangement using GAMS (General Algebraic Modeling System).

The main function in this module is:
- optimize_tables: Optimize table assignments for a given seating arrangement

This module requires GAMS to be installed and accessible from the command line.

Usage:
    This module can be run directly to test the optimization on a sample
    seating arrangement, or imported and used by other modules in the
    seating arrangement optimization system.

Note: This module generates temporary GAMS files and uses subprocess to run
GAMS commands. Ensure proper permissions and GAMS installation before use.
"""

import os
import subprocess
import importlib
from typing import Optional


def optimize_tables(seats: list[list[list[int]]]) -> Optional[list[list[list[int]]]]:
    """
    Optimize table assignments for a given seating arrangement using GAMS.

    Args:
        seats (list[list[list[int]]]): A 3D list representing the seating
            arrangement. The dimensions represent: [hanchan][table][seat]

    Returns:
        Optional[list[list[list[int]]]]: Optimized seating arrangement with
        table assignments, or None if optimization fails.
    """
    table_count = len(seats[0])
    hanchan_count = len(seats)
    table_max = (table_count + hanchan_count - 1) // table_count
    N = table_count * 4

    # Write GAMS file
    gams_file = f"optimize_{N}.gms"
    with open(gams_file, "w") as f:
        f.write(_generate_gams_model(hanchan_count, table_count, table_max, N))

    # Write seats data to GDX
    _write_seats_to_gdx(seats, N, hanchan_count, table_count)

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
    _process_gams_output(process)

    # Check if results file exists
    if not os.path.exists(f"results_{N}.txt"):
        print("No results file found. GAMS optimization may have failed.")
        return None

    # Read and process results
    new_seats = _process_results(N, hanchan_count, table_count)

    # Write new seats to Python file
    _write_seats_to_file(N, hanchan_count, new_seats)

    # Clean up temporary files
    _cleanup_temp_files(N, gams_file)

    return new_seats


def _generate_gams_model(hanchan_count: int, table_count: int, table_max: int, N: int) -> str:
    """Generate the GAMS model for table optimization."""
    return f"""
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
"""


def _write_seats_to_gdx(seats: list[list[list[int]]], N: int, hanchan_count: int, table_count: int) -> None:
    """Write seats data to GDX file."""
    with open(f"seats_{N}.gms", "w") as f:
        f.write(f"""
Set
    h hanchan / 1*{hanchan_count} /
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


def _process_gams_output(process: subprocess.Popen) -> None:
    """Process and print GAMS output."""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    process.poll()


def _process_results(N: int, hanchan_count: int, table_count: int) -> list[list[list[int]]]:
    """Process optimization results and create new seating arrangement."""
    new_seats = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    with open(f"results_{N}.txt", "r") as f:
        for line in f:
            s, t, p = map(int, line.split())
            new_seats[s-1][t-1].append(p)
    return new_seats


def _write_seats_to_file(N: int, hanchan_count: int, new_seats: list[list[list[int]]]) -> None:
    """Write optimized seating arrangement to a Python file."""
    with open(f"tables/{N}x{hanchan_count}.py", "w") as f:
        out = f"{new_seats}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")


def _cleanup_temp_files(N: int, gams_file: str) -> None:
    """Clean up temporary files created during optimization."""
    for file in [gams_file, f"seats_{N}.gms", f"seats_{N}.gdx", f"results_{N}.txt",
                 f"optimize_{N}.lst", f"seats_{N}.lst"]:
        if os.path.exists(file):
            os.remove(file)


def _make_stats(seats: list[list[list[int]]]) -> dict[str, str]:
    """Calculate statistics for a seating arrangement."""
    from stats import make_stats
    stats = make_stats(seats)
    table_visits = stats[stats.find("Table Visit frequencies:"):stats.find("Wind frequencies:")]
    return {"table_visits": table_visits}


if __name__ == "__main__":
    # Example usage
    from stats import make_stats
    sample_seats = importlib.import_module("meetups.60x8").seats
    optimized_seats = optimize_tables(sample_seats)
    if optimized_seats:
        print("Optimization successful")
        original_stats = _make_stats(sample_seats)
        optimized_stats = _make_stats(optimized_seats)
        print(f"Original table visits:\n{original_stats['table_visits']}")
        print(f"Optimized table visits:\n{optimized_stats['table_visits']}")
    else:
        print("Optimization failed")
