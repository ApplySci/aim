import importlib
from itertools import combinations
import os
import subprocess


print("add a command-line argument to suppress re-running coptic, thus re-using previous coptic outputs")

tables = 8
total_rounds = 10
hanchan = 8
players = tables * 4

use_coptic : bool = len(os.sys.argv) < 2

seats = importlib.import_module(f"{players}")

initial_seating = ''
for k in list(range(0, total_rounds)):
    initial_seating += '{\n'
    for r in seats.seats[k]:
        initial_seating += ' {'
        for p in r:
            initial_seating += f' {p-1},'
        initial_seating = initial_seating[:-1] + ' },\n'
    initial_seating = initial_seating[:-1] + ' },\n'
initial_seating = initial_seating[:-1]

with open('template.c', 'r') as file:
    raw_template = file.read()

base_template = raw_template.replace(
    '#HANCHAN#', str(hanchan)).replace(
    '#TABLES#', str(tables)).replace(
    '#INITIAL_SEATING#', initial_seating).replace(
    '#TOTAL_ROUNDS#', str(total_rounds)
    )

c_file = 'coptic.c'

results = []
# Generate all combinations of (N-M) objects
for combo in combinations(range(total_rounds), hanchan):
    template = base_template.replace('#HANCHAN#', str(hanchan))
    idx = ''.join(str(i) for i in combo)
    coptic_file = f"coptic.coptic/{idx}.txt"

    if use_coptic:
        rounds_to_use =  ', '.join(str(i) for i in combo)

        c_source = template.replace('#ROUNDS_TO_USE#', rounds_to_use)
        with open(c_file, 'w') as file:
            file.write(c_source)

        # Execute the perl script
        subprocess.run(['../tool/coptic.pl', c_file])

        # TODO catch if file doesn't exist - no solution found
        os.rename('coptic.coptic/default.txt', coptic_file)

    # Run the C program 'shuffle' and redirect output to file
    outfile = f"out/{idx}.txt"
    with open(outfile, 'w') as f:
        subprocess.run(['./shuffle', coptic_file], stdout=f)
    with open(outfile, 'r') as f:
        for line in f:
            if "FINAL SCORE" in line:
                results.append((line.split('FINAL')[1].strip(), outfile))
                break

    # if score was zero we can halt now
    parts = line.split("FINAL SCORE:")

    # The second part should contain the score as a string with leading spaces
    score_str = parts[1]

    # Strip leading/trailing spaces and convert to integer
    score = int(score_str.strip())
    if score == 0:
        break

results.sort()
file = results[0][1]

# Start and end patterns
start = "SEATING BY ROUND, BY TABLE"
end = "TABLE COUNT BY PLAYER"

# Print lines between start and end patterns
flag = False
with open(file, 'r') as f, open(f'seats_{players}x{hanchan}.py', 'w') as out:
    for line in f:
        if start in line:
            flag = True
            continue
        if end in line:
            flag = False
        if flag:
            out.write(line)
