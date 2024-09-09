import importlib
import os

from meets import optimize_meets
from stats import make_stats


def loop_all():
    if os.path.exists("all.log"):
        os.remove("all.log")
    for tables in range(4,23):
        print(f"\n\n*****************************\ntables={tables}\n\n")
        seats_module = importlib.import_module(f"sgp.{4*tables}")        
        all_seats = seats_module.seats
        max_hanchan = len(all_seats)
        for hanchan in range(2, max_hanchan+1):
            try:
                run = f"{tables*4}x{hanchan}"
                if os.path.exists(f"meetups/{run}.py"):
                    seats = importlib.import_module(f"meetups.{run}").seats
                else:
                    seats = optimize_meets(all_seats, hanchan)
                out = make_stats(seats)
                log = out[out.find("Indirect Meetup frequencies:"):]
                print(log)
                with open("all.log", "a") as f:
                    f.write(log)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    loop_all()