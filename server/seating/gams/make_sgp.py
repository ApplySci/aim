"""
Seating Generation Problem (SGP) Solver

This module provides functionality to solve the Seating Generation Problem
using GAMS (General Algebraic Modeling System). It generates optimal seating
arrangements for a given number of players and rounds (hanchans).

The main function in this module is:
- solve_sgp: Solve the Seating Generation Problem for given parameters

This module requires GAMS to be installed and accessible from the command line.

Usage:
    This module can be run directly with command-line arguments to generate
    seating arrangements, or imported and used by other modules in the
    seating arrangement optimization system.

Note: This module generates temporary GAMS files and uses subprocess to run
GAMS commands. Ensure proper permissions and GAMS installation before use.
"""

import argparse
import os
import subprocess
import sys
from typing import List, Optional


def solve_sgp(hanchan_count: int, player_count: int) -> Optional[List[List[List[int]]]]:
    """
    Solve the Seating Generation Problem (SGP) using GAMS.

    Args:
        hanchan_count (int): Number of rounds (hanchans)
        player_count (int): Number of players

    Returns:
        Optional[List[List[List[int]]]]: Optimized seating arrangement,
        or None if optimization fails
    """
    table_count = player_count // 4
    N = player_count

    # Write GAMS file
    gams_file = f"sgp_{N}x{hanchan_count}.gms"
    with open(gams_file, "w") as f:
        f.write(_generate_gams_model(hanchan_count, N, table_count))

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
    results_file = f"sgp_results_{N}x{hanchan_count}.txt"
    if not os.path.exists(results_file):
        print("No results file found. GAMS optimization may have failed.")
        return None

    # Read results
    seats = _process_results(results_file, hanchan_count, table_count)

    # Write seats to Python file
    _write_seats_to_file(N, hanchan_count, seats)

    # Clean up temporary files
    _cleanup_temp_files(N, hanchan_count, gams_file, results_file)

    return seats


def _generate_gams_model(hanchan_count: int, N: int, table_count: int) -> str:
    """Generate the GAMS model for the Seating Generation Problem."""
    return f"""
Sets
    h hanchan / 1*{hanchan_count} /
    p players / 1*{N} /
    t tables / 1*{table_count} /
    s seats / 1*4 /;

Alias(p,p1);

Binary Variables
    y(h,p,t) "1 if player p is assigned to table t in hanchan h otherwise 0"
    x(h,p,p1) "1 if players p and p1 are at the same table in hanchan h";

Variables
    z "objective value";

Equations
    obj "objective function"
    four_players_per_table(h,t) "each table has exactly 4 players"
    one_table_per_player(h,p) "each player assigned to one table per hanchan"
    define_x(h,p,p1,t) "define x based on y"
    symmetry_x(h,p,p1) "ensure symmetry of x"
    no_self_pairing(h,p) "player cannot pair with themselves"
    pair_meets_once(p,p1) "each pair of players meets at most once";

obj.. z =e= sum((h,p,p1)$(ord(p) < ord(p1)), x(h,p,p1));

four_players_per_table(h,t).. sum(p, y(h,p,t)) =e= 4;

one_table_per_player(h,p).. sum(t, y(h,p,t)) =e= 1;

define_x(h,p,p1,t)$(ord(p) < ord(p1)).. x(h,p,p1) =g= y(h,p,t) + y(h,p1,t) - 1;

symmetry_x(h,p,p1)$(ord(p) < ord(p1)).. x(h,p,p1) =e= x(h,p1,p);

no_self_pairing(h,p).. x(h,p,p) =e= 0;

pair_meets_once(p,p1)$(ord(p) < ord(p1)).. sum(h, x(h,p,p1)) =l= 1;

Model sgp /all/;

Option optcr = 0.0;
Option threads = 4;
Option resLim = 9800;

Solve sgp using mip minimizing z;

file results / 'sgp_results_{N}x{hanchan_count}.txt' /;
put results;
loop((h,p,t)$(y.l(h,p,t) > 0.5),
    put h.tl, ' ', ord(t):0:0, ' ', p.tl /;
);
putclose;
"""


def _process_gams_output(process: subprocess.Popen) -> None:
    """Process and print GAMS output."""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    process.poll()


def _process_results(
    results_file: str,
    hanchan_count: int,
    table_count: int
) -> List[List[List[int]]]:
    """Process optimization results and create seating arrangement."""
    seats = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    with open(results_file, "r") as f:
        for line in f:
            h, t, p = map(int, line.split())
            seats[h-1][t-1].append(p)
    return seats


def _write_seats_to_file(
    N: int,
    hanchan_count: int,
    seats: List[List[List[int]]]
) -> None:
    """Write optimized seating arrangement to a Python file."""
    output_file = f"sgp/{N}x{hanchan_count}.py"
    with open(output_file, "w") as f:
        out = f"{seats}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")


def _cleanup_temp_files(
    N: int,
    hanchan_count: int,
    gams_file: str,
    results_file: str
) -> None:
    """Clean up temporary files created during optimization."""
    for file in [gams_file, results_file, f"sgp_{N}x{hanchan_count}.lst"]:
        if os.path.exists(file):
            os.remove(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Solve the Seating Generation Problem (SGP) using GAMS."
    )
    
    # Positional arguments
    parser.add_argument(
        "player_count",
        type=int,
        nargs="?",
        default=100,
        help="Number of players. Default is 100."
    )
    parser.add_argument(
        "hanchan_count",
        type=int,
        nargs="?",
        default=15,
        help="Number of hanchans (rounds). Default is 15."
    )
    
    # Optional arguments
    parser.add_argument(
        "-n",
        "--hanchan",
        type=int,
        dest="hanchan_count",
        help="Number of hanchans (rounds). Overrides positional argument."
    )
    parser.add_argument(
        "-p",
        "--players",
        type=int,
        dest="player_count",
        help="Number of players. Overrides positional argument."
    )
    
    args = parser.parse_args()

    fn = f"{args.player_count}x{args.hanchan_count}"
    if os.path.exists(f"sgp/{fn}.py"):
        print('Output file already exists: delete and rerun to re-optimize')
        sys.exit()

    result = solve_sgp(args.hanchan_count, args.player_count)

    if result:
        print(f"SGP solution saved to sgp/{fn}.py")
    else:
        print("Failed to find a solution")