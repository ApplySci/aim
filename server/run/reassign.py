from collections import defaultdict
import random
import time

from ortools.sat.python import cp_model


def fill_table_gaps(
    seats: list[list[list[int]]],
    fixed_rounds: int,
    omit_players: list[int],
    substitutes: list[int],
    time_limit_seconds: int,
) -> list[list[list[int]]]:
    """
    Optimise the seating arrangements for all hanchan, keeping the first few
    rounds unchanged, and moving players between tables to fill the gaps.

    We are going to move some players between tables, and empty some tables.

    We empty a table by making it equal to [0,0,0,0]

    Moving a player P in round X means removing them from table K,
    and putting them into table L, where L is not K.

    We will then do an optimmization which moves players between tables,
    to ensure that either a table is all zeros, or it has no zeros.

    The objectives are:
    - move as few players as possible
    - minimise the number of repeat meets (as we do in extend_meets.py)

    Args:
        seating (List[List[List[int]]]): A 3D list representing the seating
            arrangement. The dimensions represent: [hanchan][table][list of 4 players]
        fixed_rounds (int): The number of rounds to keep unchanged.
        omit_players (list[int]): The players to omit from the seating
            arrangement.
        substitutes (list[int]): The players to substitute for the omitted
            players.
        time_limit_seconds (int): The time limit for the optimisation.


    Returns:
        (List[List[List[int]]]): The optimised seating arrangement.

    """

    number_of_players_to_directly_substitute = len(omit_players) % 4

    for r in range(fixed_rounds, len(seats)):
        for t in range(len(seats[r])):
            for p in range(len(omit_players)):
                s = seats[r][t].index(omit_players[p])
                if s >= 0:
                    seats[r][t][s] = (
                        substitutes[p]
                        if p < number_of_players_to_directly_substitute
                        else 0
                    )

    # Optimization
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds

    num_rounds = len(seats)
    num_tables = len(seats[0])
    num_players = max(max(max(table) for table in round) for round in seats)

    # Decision variables
    x = {}
    for r in range(fixed_rounds, num_rounds):
        for t in range(num_tables):
            for p in range(1, num_players + 1):
                x[r, t, p] = model.NewBoolVar(f"x[{r},{t},{p}]")

    # Constraints
    for r in range(fixed_rounds, num_rounds):
        for t in range(num_tables):
            # Each table must have either 0 or 4 players
            model.Add(
                sum(x[r, t, p] for p in range(1, num_players + 1)) == 4
            ).OnlyEnforceIf(model.NewBoolVar(f"table_used[{r},{t}]"))
            model.Add(
                sum(x[r, t, p] for p in range(1, num_players + 1)) == 0
            ).OnlyEnforceIf(model.NewBoolVar(f"table_empty[{r},{t}]"))

        # Each player must be assigned to exactly one table per round
        for p in range(1, num_players + 1):
            if p not in omit_players:
                model.Add(sum(x[r, t, p] for t in range(num_tables)) == 1)

    # Objective function
    penalty = model.NewIntVar(0, 1000000, "penalty")
    meetings3 = {}
    meetings4 = {}

    for r in range(fixed_rounds, num_rounds):
        for t in range(num_tables):
            for p1 in range(1, num_players - 2):
                for p2 in range(p1 + 1, num_players - 1):
                    for p3 in range(p2 + 1, num_players):
                        group3 = (p1, p2, p3)
                        if group3 not in meetings3:
                            meetings3[group3] = model.NewIntVar(
                                0, num_rounds, f"meetings3[{group3}]"
                            )
                        model.Add(
                            meetings3[group3] == meetings3[group3] + 1
                        ).OnlyEnforceIf([x[r, t, p1], x[r, t, p2], x[r, t, p3]])

            for p1 in range(1, num_players - 3):
                for p2 in range(p1 + 1, num_players - 2):
                    for p3 in range(p2 + 1, num_players - 1):
                        for p4 in range(p3 + 1, num_players):
                            group4 = (p1, p2, p3, p4)
                            if group4 not in meetings4:
                                meetings4[group4] = model.NewIntVar(
                                    0, num_rounds, f"meetings4[{group4}]"
                                )
                            model.Add(
                                meetings4[group4] == meetings4[group4] + 1
                            ).OnlyEnforceIf(
                                [x[r, t, p1], x[r, t, p2], x[r, t, p3], x[r, t, p4]]
                            )

    penalty_terms = []
    for group, count in meetings3.items():
        penalty_terms.append(model.NewIntVar(0, num_rounds, f"penalty3[{group}]"))
        model.Add(penalty_terms[-1] == model.Max(0, count - 1))

    for group, count in meetings4.items():
        penalty_terms.append(model.NewIntVar(0, num_rounds * 10, f"penalty4[{group}]"))
        model.Add(penalty_terms[-1] == 10 * model.Max(0, count - 1))

    model.Add(penalty == sum(penalty_terms))
    model.Minimize(penalty)

    # Solve the model
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Update the seats with the optimized solution
        for r in range(fixed_rounds, num_rounds):
            for t in range(num_tables):
                seats[r][t] = [
                    p
                    for p in range(1, num_players + 1)
                    if solver.Value(x[r, t, p]) == 1
                ]
                if len(seats[r][t]) == 0:
                    seats[r][t] = [0, 0, 0, 0]
    else:
        print("No optimal or feasible solution found within the time limit.")

    return seats
