import os
import subprocess
import importlib

def extend_meets(player_count, hanchan_count):
    # Read the original seating arrangement
    module_name = f"sgp.{player_count}"
    original_seats = importlib.import_module(module_name).seats
    
    # Calculate the number of tables and original hanchan count
    table_count = len(original_seats[0])
    original_hanchan_count = len(original_seats)
    
    # Write GAMS file
    gams_file = f"extend_{player_count}x{hanchan_count}.gms"
    with open(gams_file, "w") as f:
        f.write(f"""
Sets
    h hanchan / 1*{hanchan_count} /
    t tables / 1*{table_count} /
    p players / 1*{player_count} /
    oh original_hanchan / 1*{original_hanchan_count} /;

Alias (p, p1, p2, p3, p4);

Parameters
    original_seats(oh,t,p) original seating arrangement
    /
""")
        for h, hanchan in enumerate(original_seats, 1):
            for t, table in enumerate(hanchan, 1):
                for p in table:
                    f.write(f"    {h}.{t}.{p} 1\n")
        f.write("/;\n")

        f.write("""
Binary Variables
    x(h,t,p) 'player p is seated at table t in hanchan h'
    y(p,p1) 'player p is mapped to original player p1'
    z 'objective variable';

Variables
    penalty 'penalty for repeated meetings';

Equations
    obj 'objective function'
    one_seat_per_player(h,p) 'each player is seated once per hanchan'
    four_players_per_table(h,t) 'each table has exactly 4 players'
    one_to_one_mapping(p) 'each player is mapped to exactly one original player'
    one_to_one_mapping_reverse(p1) 'each original player is mapped to exactly one player'
    first_half_seating(h,t,p) 'seating arrangement for first half follows original arrangement'
    second_half_seating(h,t,p) 'seating arrangement for second half follows remapped original arrangement'
    calculate_penalty 'calculate penalty for repeated meetings';

obj.. z =e= penalty;

one_seat_per_player(h,p).. sum(t, x(h,t,p)) =e= 1;

four_players_per_table(h,t).. sum(p, x(h,t,p)) =e= 4;

one_to_one_mapping(p).. sum(p1, y(p,p1)) =e= 1;

one_to_one_mapping_reverse(p1).. sum(p, y(p,p1)) =e= 1;

first_half_seating(h,t,p)$(ord(h) <= card(oh)).. x(h,t,p) =e= original_seats(h,t,p);

second_half_seating(h,t,p)$(ord(h) > card(oh)).. 
    x(h,t,p) =e= sum(p1, y(p,p1) * original_seats(h-card(oh),t,p1));

calculate_penalty.. 
    penalty =e= sum((h,t,p1,p2,p3,p4)$(ord(p1) < ord(p2) and ord(p2) < ord(p3) and ord(p3) < ord(p4)),
        prod(h1$(ord(h1) < ord(h)), x(h1,t,p1) * x(h1,t,p2) * x(h1,t,p3) * x(h1,t,p4)) * 
        x(h,t,p1) * x(h,t,p2) * x(h,t,p3) * x(h,t,p4));

Model extend_meets /all/;

Option optcr = 0.0;
Option threads = 4;
Option reslim = 3600;

Solve extend_meets using mip minimizing z;

file results / 'results_{player_count}x{hanchan_count}.txt' /;
put results;
loop((h,t,p)$(x.l(h,t,p) > 0.5),
    put h.tl, ' ', t.tl, ' ', p.tl /;
);
putclose;
""")

    # Run GAMS optimization
    result = subprocess.run(["gams", gams_file], capture_output=True, text=True)

    # Check if results file exists
    results_file = f"results_{player_count}x{hanchan_count}.txt"
    if not os.path.exists(results_file):
        print(f"Error: Results file {results_file} was not created.")
        return None

    # Read results and create new seating arrangement
    new_seats = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    with open(results_file, "r") as f:
        for line in f:
            h, t, p = map(int, line.split())
            new_seats[h-1][t-1].append(p)

    # Write new seats to Python file
    output_file = f"meets/{player_count}x{hanchan_count}.py"
    with open(output_file, "w") as f:
        out = f"{new_seats}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")

    # Clean up temporary files
    for file in [gams_file, f"extend_{player_count}x{hanchan_count}.lst", results_file]:
        if os.path.exists(file):
            os.remove(file)

    return new_seats

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python extend_meets.py <player_count> <hanchan_count>")
        sys.exit(1)
    
    player_count = int(sys.argv[1])
    hanchan_count = int(sys.argv[2])
    
    result = extend_meets(player_count, hanchan_count)
    
    if result:
        print(f"Extended seating arrangement saved to meets/{player_count}x{hanchan_count}.py")
    else:
        print("Failed to find a solution")
