import importlib
import os

from stats import make_stats
from make_meets import optimize_meets
from make_tables import optimize_tables
from make_winds import optimize_winds


def loop_all():
    if os.path.exists("all.log"):
        os.remove("all.log")
    for tables in range(4,23):
        print(f"\n\n*****************************\ntables={tables}\n\n")
        seats_module = importlib.import_module(f"sgp.{4*tables}")
        all_seats = seats_module.seats
        max_hanchan = len(all_seats)
        for hanchan in range(2, max_hanchan+1):
            fn = f"{tables*4}x{hanchan}"
            try:
                if os.path.exists(f"final/{fn}.py"):
                    winds = importlib.import_module(f"final.{fn}").seats
                else:
                    if os.path.exists(f"tables/{fn}.py"):
                        seats = importlib.import_module(f"es.{tables*4}x{hanchan}").seats
                    else:
                        if os.path.exists(f"meets/{fn}.py"):
                            seats = importlib.import_module(f"meets.{fn}").seats
                        else:
                            seats = optimize_meets(all_seats, hanchan)
                        seats = optimize_tables(seats)
                    winds = optimize_winds(seats)
                log = make_stats(winds)
                print(log)
                with open("all.log", "a") as f:
                    f.write(log)
            except:
                pass


if __name__ == "__main__":
    loop_all()