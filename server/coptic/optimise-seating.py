import importlib
import os
import subprocess
from glob import glob


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
    template = file.read()

template = template.replace(
    '#HANCHAN#', str(hanchan)).replace(
    '#TABLES#', str(tables)).replace(
    '#INITIAL_SEATING#', initial_seating).replace(
    '#TOTAL_ROUNDS#', str(total_rounds)
    )

for i in range(total_rounds - 1):
    # Inner loop
    for j in range(i+1, total_rounds):
        if use_coptic:

            rounds_to_use = ''
            for r in list(range(0, i)) + list(range(i+1, j)) \
                    + list(range(j+1, total_rounds)):
                rounds_to_use += f'{r}, '
            rounds_to_use  = rounds_to_use[:-2]

            c_file = template.replace('#ROUNDS_TO_USE#', rounds_to_use)
            with open('coptic.c', 'w') as file:
                file.write(c_file)

            # Execute the perl script
            subprocess.run(['../tool/coptic.pl', 'coptic.c'])

            os.rename('coptic.coptic/default.txt', f"coptic.coptic/{i}{j}.txt")

        # Run the C program 'shuffle' and redirect output to file
        subprocess.run(['./shuffle', f"coptic.coptic/{i}{j}.txt"], stdout=open(f"out/{i}{j}.txt", 'w'))

results = []
for file in glob('out/*.txt'):
    with open(file, 'r') as f:
        for line in f:
            if "FINAL SCORE" in line:
                results.append((line.split('FINAL')[1].strip(), file))

results.sort()
with open('results.txt', 'w', encoding='utf-8') as f:
    for result in results:
        f.write(f"FINAL{result[0]} in {result[1]}\n")
print(results[0])

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
