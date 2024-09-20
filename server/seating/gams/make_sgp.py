import argparse
import os
import subprocess
import sys

def solve_sgp(hanchan_count, player_count):
    table_count = player_count // 4
    N = player_count

    # Write GAMS file
    gams_file = f"sgp_{N}x{hanchan_count}.gms"
    with open(gams_file, "w") as f:
        f.write(f"""
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
""")

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
    results_file = f"sgp_results_{N}x{hanchan_count}.txt"
    if not os.path.exists(results_file):
        print("No results file found. GAMS optimization may have been interrupted or failed.")
        return None

    # Read results
    seats = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    with open(results_file, "r") as f:
        for line in f:
            h, t, p = map(int, line.split())
            seats[h-1][t-1].append(p)

    # Write seats to Python file
    output_file = f"sgp/{N}x{hanchan_count}.py"
    with open(output_file, "w") as f:
        out = f"{seats}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")

    # Clean up temporary files
    for file in [gams_file, results_file, f"sgp_{N}x{hanchan_count}.lst"]:
        if os.path.exists(file):
            os.remove(file)

    return seats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve the Seating Generation Problem (SGP) using GAMS.")
    
    # Positional arguments
    parser.add_argument("player_count", type=int, nargs="?", default=100,
                        help="Number of players. Default is 100.")
    parser.add_argument("hanchan_count", type=int, nargs="?", default=15,
                        help="Number of hanchans (rounds). Default is 15.")
    
    # Optional arguments
    parser.add_argument("-n", "--hanchan", type=int, dest="hanchan_count",
                        help="Number of hanchans (rounds). Overrides positional argument.")
    parser.add_argument("-p", "--players", type=int, dest="player_count",
                        help="Number of players. Overrides positional argument.")
    
    args = parser.parse_args()

    fn = f"{args.player_count}x{args.hanchan_count}"
    if os.path.exists(f"sgp/{fn}.py"):
        print('output file already exists: delete and rerun to re-optimise')
        sys.exit()

    result = solve_sgp(args.hanchan_count, args.player_count)

    if result:
        print(f"SGP solution saved to sgp/{fn}.py")
    else:
        print("Failed to find a solution")
