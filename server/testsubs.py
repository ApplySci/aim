from run.reassign import fill_table_gaps
from seating.gams.make_stats import make_stats
from seating.seats_8 import seats as all_seats

nTables = 7
seats_in = all_seats[nTables*4]
seats_out = fill_table_gaps(
    seats=seats_in,
    fixed_rounds=5,
    omit_players=[1, 2, 3,],
    substitutes=range(nTables * 4 + 1, nTables * 4 + 4),
    time_limit_seconds=100,
    verbose=True,
)
if seats_out is not None:
    stats = make_stats(seats_out)
    print(stats)