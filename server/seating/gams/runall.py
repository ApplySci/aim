import importlib
import os

from stats import make_stats
from tables import optimize_tables
from winds import optimize_winds


def loop_all():
    if os.path.exists("all.log"):
        os.remove("all.log")
    for tables in range(8,23):
        print(f"\n\n*****************************\ntables={tables}\n\n")
        seats_module = importlib.import_module(f"sgp.{4*tables}")        
        all_seats = seats_module.seats
        max_hanchan = len(all_seats)
        for hanchan in range(2, max_hanchan+1):
            try:
                if os.path.exists(f"../{tables*4}x{hanchan}.py"):
                    winds = importlib.import_module(f"winds.{tables*4}x{hanchan}").seats
                else:
                    if not os.path.exists(f"tables/{tables*4}x{hanchan}.py"):
                        seats = optimize_tables(all_seats, hanchan)
                    else:
                        seats = importlib.import_module(f"tables.{tables*4}x{hanchan}").seats
                    winds = optimize_winds(seats)
                log = make_stats(winds)
                print(log)
                with open("all.log", "a") as f:
                    f.write(log)
            except:
                pass


if __name__ == "__main__":
    loop_all()