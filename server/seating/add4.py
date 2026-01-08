import os
import re
import sys
from typing import Dict, List


def load_rounds_from_txt(txt_path: str) -> List[List[List[int]]]:
    """Parse p12-4.txt or p12-8.txt into rounds -> tables -> players structure.

    Expected columns per line (tab or space separated):
      round, table, player1, player2, player3, player4
    """
    rounds_to_tables: Dict[int, Dict[int, List[int]]] = {}

    with open(txt_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            parts = re.split(r"\s+", line)
            if len(parts) != 6:
                raise ValueError(f"Invalid line (expected 6 columns): {raw_line!r}")

            round_num = int(parts[0])
            table_num = int(parts[1])
            players = list(map(int, parts[2:]))

            if len(players) != 4:
                raise ValueError(f"Invalid players count (expected 4): {raw_line!r}")

            if round_num not in rounds_to_tables:
                rounds_to_tables[round_num] = {}
            if table_num in rounds_to_tables[round_num]:
                raise ValueError(f"Duplicate entry for round {round_num}, table {table_num}")
            rounds_to_tables[round_num][table_num] = players

    # Convert to ordered rounds list: [[tables...], [tables...], ...]
    rounds: List[List[List[int]]] = []
    for r in sorted(rounds_to_tables.keys()):
        tables_map = rounds_to_tables[r]
        tables: List[List[int]] = [tables_map[t] for t in sorted(tables_map.keys())]
        rounds.append(tables)

    if not rounds:
        raise ValueError("No rounds parsed from input file.")

    return rounds


def build_block_for_12(rounds: List[List[List[int]]]) -> str:
    """Builds a text block matching the formatting style in seats_4.py for key 12."""
    indent_key = "    "   # 4 spaces (indent for the key line)
    indent_inn = "     "   # 5 spaces (indent for subsequent lines within the value)

    lines: List[str] = []

    for r_index, tables in enumerate(rounds):
        if r_index == 0:
            # First round starts on the same line as the key with triple opening brackets
            first_table = tables[0]
            first_nums = ", ".join(map(str, first_table))
            lines.append(f"{indent_key}12: [[[{first_nums}]],")
            start_table_index = 1
        else:
            # Subsequent rounds each start with double opening brackets on their own line
            first_table = tables[0]
            first_nums = ", ".join(map(str, first_table))
            lines.append(f"{indent_inn}[[{first_nums}],")
            start_table_index = 1

        # Middle tables in the round (if any)
        for t in tables[start_table_index:-1]:
            nums = ", ".join(map(str, t))
            lines.append(f"{indent_inn}[{nums}],")

        # Last table for the round closes the round brackets and ends with a comma
        last_table = tables[-1]
        last_nums = ", ".join(map(str, last_table))
        lines.append(f"{indent_inn}[{last_nums}]],")

    # Add a trailing blank line to match surrounding style
    lines.append("")

    return "\n".join(lines)


def insert_block_into_seats_py(seats_py_path: str, block: str, filename: str) -> None:
    with open(seats_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # If a 12-entry already exists, do nothing
    if re.search(r"\n\s*12:\s*\[\[", content):
        print(f"Key 12 already exists in {filename}; no changes made.")
        return

    # Prefer inserting before the first key (currently 16) to keep ascending order
    m = re.search(r"\n\s*16:\s*\[\[", content)
    if m:
        insert_at = m.start() + 1  # position at start of the line that begins with spaces then 16
    else:
        # Fallback: insert immediately after 'seats = {' line
        m2 = re.search(r"seats\s*=\s*\{\s*\n", content)
        if not m2:
            raise RuntimeError(f"Could not locate 'seats = {{' in {filename}")
        insert_at = m2.end()

    new_content = content[:insert_at] + block + content[insert_at:]

    with open(seats_py_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)

    print(f"Inserted seating for 12 players into {filename}.")


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Determine which input file to use based on command line argument or default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "p12-4.txt"  # Default to 4-round format
    
    txt_path = os.path.join(base_dir, input_file)
    
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"Input file not found: {txt_path}")
    
    rounds = load_rounds_from_txt(txt_path)
    
    # Determine expected number of rounds and target seats file based on input
    if input_file == "p12-4.txt":
        expected_rounds = 4
        seats_py_path = os.path.join(base_dir, "seats_4.py")
        seats_filename = "seats_4.py"
    elif input_file == "p12-8.txt":
        expected_rounds = 8
        seats_py_path = os.path.join(base_dir, "seats_8.py")
        seats_filename = "seats_8.py"
    else:
        # Try to infer from the number of rounds found
        num_rounds = len(rounds)
        if num_rounds == 4:
            seats_py_path = os.path.join(base_dir, "seats_4.py")
            seats_filename = "seats_4.py"
            expected_rounds = 4
        elif num_rounds == 8:
            seats_py_path = os.path.join(base_dir, "seats_8.py")
            seats_filename = "seats_8.py"
            expected_rounds = 8
        else:
            raise ValueError(f"Unsupported number of rounds: {num_rounds}. Expected 4 or 8.")
    
    # Basic validation for the expected setup
    if len(rounds) != expected_rounds:
        raise ValueError(f"Expected {expected_rounds} rounds, found {len(rounds)}")
    for idx, tables in enumerate(rounds, start=1):
        if len(tables) != 3:
            raise ValueError(f"Expected 3 tables in round {idx}, found {len(tables)}")

    block = build_block_for_12(rounds)
    insert_block_into_seats_py(seats_py_path, block, seats_filename)


if __name__ == "__main__":
    main()

