import importlib
import os
import sys

from stats import make_stats


def stat_all(path):
    if os.path.exists(f"{path}/all.log"):
        os.remove(f"{path}/all.log")

    for file in os.listdir(path):
        if file.endswith(".py"):
            run = file.split(".")[0]
            seats = importlib.import_module(f"{path}.{run}").seats
            log = make_stats(seats)
            print(log)
            with open(f"{path}/all.log", "a") as f:
                f.write(log)

if __name__ == "__main__":
    userdir = sys.argv[1]
    stat_all(userdir)
