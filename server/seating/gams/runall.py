"""
Seating Optimization Runner

This module provides functionality to run seating optimizations for various
table and hanchan combinations. It uses different optimization strategies
(meets, tables, and winds) to generate optimal seating arrangements.

The main function in this module is:
- loop_all: Iterate through different table and hanchan combinations to generate
            and optimize seating arrangements.

This module depends on optimization functions from external modules:
make_meets, make_tables, and make_winds.

Usage:
    To run the full optimization process:
    python runall.py
"""

import importlib
import os

from extend_meets import extend_all_meets
from make_meets import optimize_meets
from make_tables import optimize_tables
from make_winds import optimize_winds


def loop_all():
    """
    Iterate through different table and hanchan combinations to generate
    and optimize seating arrangements.

    This function processes various combinations of table counts and hanchan,
    applying different optimization strategies (meets, tables, and winds)
    to create optimal seating arrangements.

    The function checks for existing optimized arrangements and only
    performs optimizations for combinations that haven't been processed yet.

    Returns:
        None
    """
    if os.path.exists("all.log"):
        os.remove("all.log")

    for tables in range(4,8):
        extend_all_meets(tables*4, 10)

    for tables in range(4, 44):
        print(f"\n\n*****************************")
        print(f"tables={tables}\n\n")

        try:
            seats_module = importlib.import_module(f"sgp.{4*tables}")
        except ImportError:
            continue

        all_seats = seats_module.seats
        max_hanchan = len(all_seats)
        max_hanchan_to_process = max(11, min(16, max_hanchan + 1))

        for hanchan in range(2, max_hanchan_to_process):
            fn = f"{tables*4}x{hanchan}"

            if os.path.exists(f"final/{fn}.py"):
                winds = importlib.import_module(f"final.{fn}").seats
            else:
                if os.path.exists(f"tables/{fn}.py"):
                    seats = importlib.import_module(f"tables.{fn}").seats
                else:
                    if os.path.exists(f"meets/{fn}.py"):
                        seats = importlib.import_module(f"meets.{fn}").seats
                    else:
                        seats = optimize_meets(all_seats, hanchan)
                    seats = optimize_tables(seats)
                winds = optimize_winds(seats)


if __name__ == "__main__":
    loop_all()
