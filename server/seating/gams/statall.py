import importlib
import os
import sys

from make_stats import make_stats


def stat_all(path):
    if os.path.exists(f"{path}/all.log"):
        os.remove(f"{path}/all.log")

    import re

    # Find all files with name of the form final/{N}x{M}.py
    pattern = re.compile(r'final/(\d+)x(\d+)\.py$')
    # Extract dimensions from filenames that match the pattern
    dimensions = [pattern.match(f).groups() for f in os.listdir('final/') if pattern.match(f)]
    dimensions.sort()

    last_seats = None
    
    for dims in dimensions:
        if last_seats != dims[0]:
            table_count = len(seats[0])
            player_count = table_count * 4
            hanchan_count = len(seats)

            # take square root of player count to get a reasonable minimum for indirect
            #   meetups. Don't worry about indirect meetups for 3 or fewer hanchan
            indirect_min = int(player_count ** 0.5) if hanchan_count >= 4 else 0

            indirect_good = indirect_min + 3
            wind_min = hanchan_count // 4
            wind_max = (hanchan_count + 3) // 4
            table_max = (hanchan_count + table_count * 2 - 1) // table_count
            meet_max = 1

        seats = importlib.import_module(f"final/{dims[0]}x{dims[1]}").seats
        meet_hist, indirect_hist, t_hist, w_hist = make_stats(seats)

    for n in range(wind_min):
        if w_hist[n] > 0:
            pass # TODO record warnings

    for n in range(wind_max + 1, hanchan_count + 1):
        if w_hist[n] > 0:
            pass # TODO record warnings

    for n in range(table_max + 1, hanchan_count + 1):
        if t_hist[n] > 0:
            pass # TODO record warnings

    for n in range(meet_max + 1, hanchan_count + 1):
        if meet_hist[n] > 0:
            pass # TODO record warnings

    for n in range(0, indirect_min):
        if indirect_hist[n] > 0:
            pass # TODO record warnings

    for i, count in enumerate(indirect_hist):
        if count > 0:
            if i < indirect_good:
                pass # TODO record warnings
    
