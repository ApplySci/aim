import importlib
import os
import re
import tabulate
from make_stats import make_stats


def stat_all(write_final=False):
    player_count = None
    hanchan_count = None
    current_hanchan = None

    pattern = re.compile(r'(\d+)x(\d+)\.py$')
    dimensions = [pattern.match(f).groups()
                  for f in os.listdir('final/')
                  if pattern.match(f)]
    
    # Parse dimensions into ints and sort by hanchan_count, then player_count
    sorted_dimensions = sorted(
        [(int(players), int(hanchan)) for players, hanchan in dimensions],
        key=lambda x: (x[1], x[0])
    )

    def write_dict(hanchan_count, seats_dict, warnings):
        if not write_final:
            return
        out_file = f"../seats_{hanchan_count}.py"
        warnings_table = tabulate.tabulate(warnings, headers=['players',
            'total', 'wind', 'table', 'meet', 'indirect'
            ], tablefmt="psql")
        with open(out_file, "w") as f:
            f.write(
                f"""\
\"\"\"
*** imperfect allocations:
{warnings_table}
***
\"\"\"

seats = {{
"""
        )
        # end of the file docstring
        
            for player_count, seats in seats_dict.items():
                seats_str = str(seats).replace("],", "],\n    ")
                f.write(f"    {player_count}: {seats_str},\n\n")
            f.write("}\n")

        # end of write_dict

    for player_count, hanchan_count in sorted_dimensions:
        if hanchan_count != current_hanchan:
            if current_hanchan is not None:
                write_dict(current_hanchan, current_dict, all_warnings)
            # new output file, so reset all of the variables we accumulate stuff in
            current_hanchan = hanchan_count
            current_dict = {}
            wind_min = hanchan_count // 4
            wind_max = (hanchan_count + 3) // 4
            meet_max = 1
            total_warnings = {}
            wind_warnings = {}
            table_warnings = {}
            meet_warnings = {}
            indirect_warnings = {}
            all_warnings = []

        table_count = player_count // 4
        # take square root of player count to get a reasonable minimum for indirect
        #   meetups. Don't worry about indirect meetups for 3 or fewer hanchan
        indirect_min = int(player_count ** 0.5) if hanchan_count >= 4 else 0

        table_max = (hanchan_count + table_count * 2 - 1) // table_count

        fn = f"{player_count}x{hanchan_count}"
        seats = importlib.import_module(f"final.{fn}").seats
        current_dict[player_count] = seats
        meet_hist, indirect_hist, t_hist, w_hist = make_stats(seats)

        warnings = 0
        wind_warnings = 0
        for n in range(wind_min):
            if w_hist[n] > 0:
                wind_warnings += 1

        for n in range(wind_max + 1, hanchan_count + 1):
            if w_hist[n] > 0:
                warnings += 1

        table_warnings = 0
        for n in range(table_max + 1, hanchan_count + 1):
            if t_hist[n] > 0:
                table_warnings += 1

        meet_warnings = 0
        for n in range(meet_max + 1, hanchan_count + 1):
            if meet_hist[n] > 0:
                meet_warnings += 1

        indirect_warnings = 0
        for n in range(0, indirect_min):
            if indirect_hist[n] > 0:
                indirect_warnings += 1

        total_warnings = wind_warnings + table_warnings + meet_warnings + \
            indirect_warnings
        print(f"{fn}: {total_warnings}")

        wind_warning_text = f"{wind_warnings}/{4*player_count}" \
            if wind_warnings > 0 else ''
        table_warning_text = \
            f"{table_warnings}/{player_count * hanchan_count // 2}" \
            if table_warnings > 0 else ''
        meet_warning_text = \
            f"{meet_warnings}/{player_count * 3 * hanchan_count // 2}" \
            if meet_warnings > 0 else ''
        indirect_warning_text = \
            f"{indirect_warnings}/{player_count * (player_count-1) // 2}" \
            if indirect_warnings > 0 else ''

        all_warnings.append([player_count, total_warnings, wind_warning_text,
                        table_warning_text, meet_warning_text,
                        indirect_warning_text])
    # Write the last dictionary after the loop ends
    if current_hanchan is not None:
        write_dict(current_hanchan, current_dict, all_warnings)

if __name__ == "__main__":
    stat_all(write_final=True)