import argparse
import importlib
from itertools import combinations
from math import factorial
import os
import subprocess


#   handle the command-line arguments


parser = argparse.ArgumentParser(description="Produce an optimal seating plan")

parser.add_argument("tables", metavar="tables", type=int, nargs=1,
                    help="number of tables")

parser.add_argument("hanchan", metavar="hanchan", type=int, nargs=1,
                    help="number of hanchan")

parser.add_argument("-no", action="store_true",
                    help="don't run coptic - use previous results")

parser.add_argument("-f", "--force", action="store_true",
                    help="force re-running of coptic even if output file already exists")

args = parser.parse_args()
tables = args.tables[0]
hanchan = args.hanchan[0]
use_coptic = not args.no
force_coptic = args.force


#    write our programs from templates

players = tables * 4

# eg 5-8 hanchan, 4 tables: 2 is tolerable.
tolerable_repeats = int((hanchan + tables - 1) / tables)


seats = importlib.import_module(f"{players}")
total_rounds = len(seats.seats)

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


#  customise the shuffle program


with open('shuffle_template.c', 'r') as file:
    shuffle_template = file.read()

shuffle_source = shuffle_template.replace(
    '#HANCHAN#', str(hanchan)).replace(
    '#TABLES#', str(tables)).replace(
    '#TOLERABLE_REPEATS#', str(tolerable_repeats))

shuffle_file = 'shuffle.c'
with open(shuffle_file, 'w') as f:
    f.write(shuffle_source)

subprocess.run(['gcc', shuffle_file, '-o', 'shuffle'])


#  end of shuffle customisation


#  go over all the possible combinations of selecting the right number
#  of hanchans from the available rounds, optimising each time


c_file = 'coptic.c'

results = []
all_combos = combinations(range(total_rounds), hanchan)
best_score = 9999999

if use_coptic:
    combo_count = int(factorial(total_rounds) \
                / factorial(hanchan) \
                / factorial(total_rounds - hanchan))
    minutes = int(6 * combo_count / 60) # 6s per iteration
    print(f"{combo_count} combinations to test: estimated time: {minutes}m")

for combo in all_combos:
    template = base_template.replace('#HANCHAN#', str(hanchan))
    idx = ''.join(str(i) for i in combo)
    coptic_file = f"coptic.coptic/{idx}.txt"
    outfile = f"shuffled/{idx}.txt"

    if use_coptic and (
            force_coptic
            or not os.path.isfile(coptic_file)
            or os.path.getsize(coptic_file) == 0):

        rounds_to_use =  ', '.join(str(i) for i in combo)

        c_source = template.replace('#ROUNDS_TO_USE#', rounds_to_use)
        with open(c_file, 'w') as file:
            file.write(c_source)

        # Execute the perl script
        coptic_output = subprocess.run(
            ['../tool/coptic.pl', c_file],
            capture_output=True,
            text=True,
            )

        if not "Result: Solution: " in coptic_output.stdout:
            print('\n*** failed to find a solution\n')
            continue

        os.rename('coptic.coptic/default.txt', coptic_file)
        print('.', end='', flush=True)

    # Run the C program 'shuffle' and capture the output

    if os.path.isfile(coptic_file) and os.path.getsize(coptic_file) > 0:
        shuffle_output = subprocess.run(
                ['./shuffle', coptic_file],
                capture_output=True,
                text=True,)

    with open(outfile, 'w') as f:
        f.write(shuffle_output.stdout)

    for line in shuffle_output.stdout.split('\n'):
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
    if score < best_score:
        print(f"\nbest score to date: {score} in {idx}")
        best_score = score


#  pick our best result and save it


results.sort()
file = results[0][1]

print(f"BEST {results[0][0]} in {results[0][1]}")
# Start and end patterns
start = "SEATING BY ROUND, BY TABLE"
end = "TABLE COUNT BY PLAYER"

# Print lines between start and end patterns
flag = False
with open(file, 'r') as f, open(f'final/seats_{players}x{hanchan}.py', 'w') as out:
    for line in f:
        if start in line:
            flag = True
            continue
        if end in line:
            flag = False
        if flag:
            out.write(line)
