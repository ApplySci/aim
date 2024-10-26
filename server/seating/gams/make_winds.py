import os
import subprocess
from typing import Optional


def optimize_winds(seats: list[list[list[int]]]) -> Optional[list[list[list[int]]]]:
    """
    Optimize wind assignments for a given seating arrangement using GAMS.

    Args:
        seats (list[list[list[int]]]): A 3D list representing the seating
            arrangement. The dimensions represent: [hanchan][table][seat]

    Returns:
        Optional[list[list[list[int]]]]: Optimized seating arrangement with
        wind assignments, or None if optimization fails.
    """
    hanchan_count = len(seats)
    table_count = len(seats[0])
    N = table_count * 4

    # Write GAMS file
    gams_file = f"optimize_{N}.gms"
    with open(gams_file, "w") as f:
        f.write(_generate_gams_model(hanchan_count, table_count, N))

    # Write seats data to GDX
    _write_seats_to_gdx(seats, N, hanchan_count, table_count)

    # Run GAMS to create GDX
    subprocess.run(["gams", f"seats_{N}.gms"])

    # Run GAMS optimization
    subprocess.run(["gams", gams_file], capture_output=False, text=True)

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


def _generate_gams_model(hanchan_count: int, table_count: int, N: int) -> str:
    """Generate the GAMS model for wind optimization."""
    return f"""
$offsymxref offsymlist
Option limrow = 0;
Option limcol = 0;
Option solprint = off;
Option sysout = off;

Sets
    h hanchan / 1*{hanchan_count} /
    t tables / 1*{table_count} /
    p players / 1*{N} /
    w winds / 1*4 /;

Alias (w, w1);

Parameter seats(h,t,p);

$gdxin seats_{N}.gdx
$load seats
$gdxin

Variables
    z objective value;

Binary Variables
    x(h,t,p,w) seating arrangement;

Positive Variables
    excess(p,w) excess appearances for each player for each wind
    deficit(p,w) deficit appearances for each player for each wind;

Equations
    obj objective function
    define_excess(p,w) define excess appearances
    define_deficit(p,w) define deficit appearances
    maintain_players(h,t,p) maintain the same players at each table across hanchans
    one_wind_per_player(h,t) each player at a table must be assigned to exactly one wind
    one_player_per_wind(h,t,w) each wind at a table must be assigned to exactly one player
    first_hanchan_order(t,w,w1) enforce ascending order in first hanchan;

obj.. z =e= sum((p,w), excess(p,w) + deficit(p,w));

define_excess(p,w).. excess(p,w) =g= sum((h,t), x(h,t,p,w)) - ({hanchan_count}+3)/4;

define_deficit(p,w).. deficit(p,w) =g= {hanchan_count}/4 - sum((h,t), x(h,t,p,w));

maintain_players(h,t,p).. sum(w, x(h,t,p,w)) =e= seats(h,t,p);

one_wind_per_player(h,t).. sum((p,w), x(h,t,p,w)) =e= 4;

one_player_per_wind(h,t,w).. sum(p, x(h,t,p,w)) =e= 1;

first_hanchan_order(t,w,w1)$(ord(w) < ord(w1))..
    sum(p, ord(p) * x('1',t,p,w)) =l= sum(p, ord(p) * x('1',t,p,w1));

Model seating /all/;

Option optcr = 0.1;
Option threads = 1;
Option solvelink = 5;

$onecho > cplex.opt
names no
mipinterval 1
$offecho

seating.optfile = 1;

Solve seating using mip minimizing z;

file results / 'results_{N}.txt' /;
put results;
loop(h,
    loop(t,
        put h.tl, t.tl;
        loop(w,
            loop(p$(x.l(h,t,p,w) > 0.5),
                put ' ' p.tl;
            );
        );
        put /;
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

        f.write(f"""
execute_unload "seats_{N}.gdx" seats;
""")


def _process_results(N: int, hanchan_count: int, table_count: int) -> list[list[list[int]]]:
    """Process optimization results and create new seating arrangement."""
    new_seats = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    with open(f"results_{N}.txt", "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 6:  # Ensure we have h, t, and 4 player numbers
                h, t = int(parts[0]), int(parts[1])
                players = [int(p) for p in parts[2:]]
                new_seats[h-1][t-1] = players

    # Ensure each table has exactly 4 players
    for hanchan in new_seats:
        for table in hanchan:
            while len(table) < 4:
                table.append(0)

    return new_seats


def _write_seats_to_file(N: int, hanchan_count: int, new_seats: list[list[list[int]]]) -> None:
    """Write optimized seating arrangement to a Python file."""
    filename = f"final/{N}x{hanchan_count}.py"
    with open(filename, "w") as f:
        seats_text = f"{new_seats}".replace("],", "],\n")
        f.write(f"seats = {seats_text}\n")


def _cleanup_temp_files(N: int, gams_file: str) -> None:
    """Clean up temporary files created during optimization."""
    for file in [gams_file, f"seats_{N}.gms", f"seats_{N}.gdx", f"results_{N}.txt",
                 f"optimize_{N}.lst", f"seats_{N}.lst"]:
        if os.path.exists(file):
            os.remove(file)


if __name__ == "__main__":
    # Example usage
    sample_seats = [[[1, 2, 3, 4], [5, 6, 7, 8]], [[1, 5, 6, 7], [2, 3, 4, 8]]]
    optimized_seats = optimize_winds(sample_seats)
    if optimized_seats:
        print("Optimization successful")
        print(optimized_seats)
    else:
        print("Optimization failed")
