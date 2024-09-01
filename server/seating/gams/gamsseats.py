import importlib
import os
import subprocess
import argparse
from stats import make_stats


def optimize_winds(N, hanchan_count):
    # Import the seats data
    seats_module = importlib.import_module(f"in.seats_{N}x{hanchan_count}")
    seats = seats_module.seats

    # Calculate table_count
    table_count = N // 4

    # Write GAMS file
    gams_file = f"optimize_{N}.gms"
    with open(gams_file, "w") as f:
        f.write(f"""
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
    excess(p,w) excess appearances for each player for each wind;

Equations
    obj objective function
    define_excess(p,w) define excess appearances
    maintain_players(h,t,p) maintain the same players at each table across hanchans
    one_wind_per_player(h,t) each player at a table must be assigned to exactly one wind
    one_player_per_wind(h,t,w) each wind at a table must be assigned to exactly one player
    first_hanchan_order(t,w,w1) enforce ascending order in first hanchan;

obj.. z =e= sum((p,w), excess(p,w));

define_excess(p,w).. excess(p,w) =g= sum((h,t), x(h,t,p,w)) - ({hanchan_count}+3)/4;

maintain_players(h,t,p).. sum(w, x(h,t,p,w)) =e= seats(h,t,p);

one_wind_per_player(h,t).. sum((p,w), x(h,t,p,w)) =e= 4;

one_player_per_wind(h,t,w).. sum(p, x(h,t,p,w)) =e= 1;

first_hanchan_order(t,w,w1)$(ord(w) < ord(w1))..
    sum(p, ord(p) * x('1',t,p,w)) =l= sum(p, ord(p) * x('1',t,p,w1));

Model seating /all/;

Option optcr = 0.0;
Option threads = 4;

$log Dimensions of x:
$log %x.dim%
$log Dimensions of seats:
$log %seats.dim%
$log Contents of seats:
$log %seats%

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
""")

    # Write seats data to GDX
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

    # Run GAMS to create GDX
    subprocess.run(["gams", f"seats_{N}.gms"])

    # Run GAMS optimization
    try:
        process = subprocess.Popen(
            ["gams", gams_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        print("GAMS Output:")
        print(stdout)
        print("GAMS Errors:")
        print(stderr)

        # Print the contents of the listing file
        listing_file = f"{os.path.splitext(gams_file)[0]}.lst"
        if os.path.exists(listing_file):
            with open(listing_file, 'r') as f:
                print("GAMS Listing File:")
                print(f.read())
        else:
            print(f"Listing file {listing_file} not found.")

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

    # Write new seats to Python file
    with open(f"seats_{N}x{hanchan_count}.py", "w") as f:
        f.write(f"seats = {new_seats}\n")

    # Clean up temporary files
    for file in [gams_file, f"seats_{N}.gms", f"seats_{N}.gdx", f"results_{N}.txt",
                 f"optimize_{N}.txt"]:
        if os.path.exists(file):
            os.remove(file)

    # Run make_stats on the new arrangement
    make_stats(table_count, hanchan_count)

    return new_seats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize seating arrangement.")
    parser.add_argument("player_count", type=int, help="Number of players")
    parser.add_argument("hanchan_count", type=int, help="Number of hanchan (rounds)")
    args = parser.parse_args()

    optimize_winds(args.player_count, args.hanchan_count)
