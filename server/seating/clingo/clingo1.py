import clingo
import sys
from stats import make_stats

def generate_seating(table_count, hanchan_count):
    player_count = table_count * 4

    # Generate the Clingo program
    program = f"""
    player(1..{player_count}).
    table(1..{table_count}).
    hanchan(1..{hanchan_count}).

    1 {{ plays(P,H,T) : table(T) }} 1 :- player(P), hanchan(H).
    4 {{ plays(P,H,T) : player(P) }} 4 :- hanchan(H), table(T).

    meets(P1,P2,H) :- plays(P1,H,T), plays(P2,H,T), P1 < P2.

    % Hard constraint: No two players should meet more than 2 times
    :- player(P1), player(P2), P1 < P2, #count {{ H : meets(P1,P2,H) }} > 2.

    % Soft constraint: Minimize repeated meetings
    :~ #sum {{ 1,P1,P2 : meets(P1,P2,H), H = 2..{hanchan_count} }} > 0. [1]

    % Soft constraint: Minimize number of visits to a table by a player beyond 3
    :~ player(P), table(T), #count {{ H : plays(P,H,T) }} > 3. [1,P,T]

    #show plays/3.
    """

    # Create a Control object
    ctl = clingo.Control()

    # Add the program to the control object
    ctl.add("base", [], program)

    # Ground the program
    ctl.ground([("base", [])])

    # Initialize the result structure
    result = []

    # Solve the program
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            # Initialize the hanchan structure
            hanchan_structure = [[] for _ in range(hanchan_count)]
            
            for atom in model.symbols(shown=True):
                if atom.name == "plays":
                    player, hanchan, table = [arg.number for arg in atom.arguments]
                    
                    # Adjust indices to be 0-based
                    hanchan_index = hanchan - 1
                    table_index = table - 1
                    
                    # Ensure the table exists in the hanchan
                    while len(hanchan_structure[hanchan_index]) <= table_index:
                        hanchan_structure[hanchan_index].append([])
                    
                    # Add the player to the table
                    hanchan_structure[hanchan_index][table_index].append(player)
            
            # Sort players within each table
            for hanchan in hanchan_structure:
                for table in hanchan:
                    table.sort()
            
            result.append(hanchan_structure)
            break  # We only need one solution

    # Save the result to a file
    output_filename = f'seats_{player_count}x{hanchan_count}.py'
    if result:
        with open(output_filename, 'w') as f:
            f.write("seats = [\n")
            for hanchan in result[0]:
                f.write("    [\n")
                for table in hanchan:
                    f.write(f"    {table},\n")
                f.write("    ],\n")
            f.write("]\n")
        print(f"Results saved to {output_filename}")
        make_stats(table_count, hanchan_count)
    else:
        print("No solution found.")

    return result

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_seating.py <table_count> <hanchan_count>")
        sys.exit(1)
    
    try:
        table_count = int(sys.argv[1])
        hanchan_count = int(sys.argv[2])
    except ValueError:
        print("Error: Both arguments must be integers.")
        sys.exit(1)
    
    generate_seating(table_count, hanchan_count)

# Example usage
# generate_seating(7, 10)