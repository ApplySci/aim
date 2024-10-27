from run.reassign import fill_table_gaps
from seating.gams.make_stats import make_stats
from seating.seats_10 import seats as all_seats


def print_callback(message, end="\n"):
    print(message, end=end, flush=True)


nTables = 12
seats_in = all_seats[nTables * 4]
subs = [p for p in range(nTables * 4 + 1, nTables * 4 + 4)]
seats_out = fill_table_gaps(
    seats=seats_in,
    fixed_rounds=4,
    omit_players=[1, 12, 23, 34, 5, 16],
    substitutes=subs,
    time_limit_seconds=10,
    verbose=True,
    log_callback=print_callback,
)
print(make_stats(seats_out, [0, *subs]))
for rnd in seats_out:
    print("======")
    for tbl in rnd:
        print(tbl)
