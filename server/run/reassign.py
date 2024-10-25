from collections import defaultdict
import random
import sys
import time

from ortools.sat.python import cp_model


def fill_table_gaps(
    seats: list[list[list[int]]],
    fixed_rounds: int,
    omit_players: list[int],
    substitutes: list[int],
    time_limit_seconds: int,
    verbose: bool = False,
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
        verbose (bool): Whether to print progress updates.


    Returns:
        (List[List[List[int]]]): The optimised seating arrangement.

    """
    print('preparing solver')
    number_of_players_to_directly_substitute = len(omit_players) % 4

    for r in range(fixed_rounds, len(seats)):
        for t in range(len(seats[r])):
            for p in range(len(omit_players)):
                if omit_players[p] in seats[r][t]:
                    s = seats[r][t].index(omit_players[p])
                    seats[r][t][s] = (
                        substitutes[p]
                        if p < number_of_players_to_directly_substitute
                        else 0
                    )

    # Optimization
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.log_search_progress = verbose

    num_rounds = len(seats)
    num_tables = len(seats[0])
    num_players = number_of_players_to_directly_substitute + 4 * len(seats[0])

    # Decision variables
    x = {}
    for r in range(fixed_rounds, num_rounds):
        for t in range(num_tables):
            for p in range(1, num_players + 1):
                if p not in omit_players:
                    x[r, t, p] = model.NewBoolVar(f"x[{r},{t},{p}]")

    # Constraints
    for r in range(fixed_rounds, num_rounds):
        for t in range(num_tables):
            # Each table must have either 0 or 4 players
            table_players = [x[r, t, p] for p in range(1, num_players + 1) if p not in omit_players]
            model.Add(sum(table_players) == 4).OnlyEnforceIf(model.NewBoolVar(f"table_used[{r},{t}]"))
            model.Add(sum(table_players) == 0).OnlyEnforceIf(model.NewBoolVar(f"table_empty[{r},{t}]"))

        # Each player must be assigned to exactly one table per round
        for p in range(1, num_players + 1):
            if p not in omit_players:
                model.Add(sum(x[r, t, p] for t in range(num_tables)) == 1)

    # Objective function
    penalty = model.NewIntVar(0, 1000000, "penalty")
    meetings2 = defaultdict(lambda: model.NewIntVar(0, num_rounds, "meetings2"))
    meetings3 = defaultdict(lambda: model.NewIntVar(0, num_rounds, "meetings3"))
    meetings4 = defaultdict(lambda: model.NewIntVar(0, num_rounds, "meetings4"))

    # Count meetings for fixed rounds (to be used as a baseline)
    fixed_meetings2 = defaultdict(int)
    fixed_meetings3 = defaultdict(int)
    fixed_meetings4 = defaultdict(int)

    for r in range(fixed_rounds):
        for t in range(num_tables):
            table_players = seats[r][t]
            for i in range(len(table_players)):
                for j in range(i+1, len(table_players)):
                    p1, p2 = table_players[i], table_players[j]
                    group2 = tuple(sorted([p1, p2]))
                    fixed_meetings2[group2] += 1

                for k in range(j+1, len(table_players)):
                    p1, p2, p3 = table_players[i], table_players[j], table_players[k]
                    group3 = tuple(sorted([p1, p2, p3]))
                    fixed_meetings3[group3] += 1

            if len(table_players) == 4:
                group4 = tuple(sorted(table_players))
                fixed_meetings4[group4] += 1

    # Count meetings for variable rounds
    for r in range(fixed_rounds, num_rounds):
        print(f'\nround {r+1}, table ', end='')
        for t in range(num_tables):
            print(f'{t+1},', end='')
            sys.stdout.flush()
            table_players = [p for p in range(1, num_players + 1) if p not in omit_players]
            for i in range(len(table_players)):
                for j in range(i+1, len(table_players)):
                    p1, p2 = table_players[i], table_players[j]
                    group2 = tuple(sorted([p1, p2]))
                    model.Add(meetings2[group2] == meetings2[group2] + 1).OnlyEnforceIf([x[r, t, p1], x[r, t, p2]])

                    for k in range(j+1, len(table_players)):
                        p1, p2, p3 = table_players[i], table_players[j], table_players[k]
                        group3 = tuple(sorted([p1, p2, p3]))
                        model.Add(meetings3[group3] == meetings3[group3] + 1).OnlyEnforceIf([x[r, t, p1], x[r, t, p2], x[r, t, p3]])

            if len(table_players) >= 4:
                for j in range(i+1, len(table_players)):
                    for k in range(j+1, len(table_players)):
                        for l in range(k+1, len(table_players)):
                            p1, p2, p3, p4 = table_players[i], table_players[j], table_players[k], table_players[l]
                            group4 = tuple(sorted([p1, p2, p3, p4]))
                            model.Add(meetings4[group4] == meetings4[group4] + 1).OnlyEnforceIf([x[r, t, p1], x[r, t, p2], x[r, t, p3], x[r, t, p4]])

    penalty_terms = []
    for group, count in meetings2.items():
        penalty_term = model.NewIntVar(0, num_rounds, f"penalty2_{group}")
        model.Add(penalty_term >= count - max(1, fixed_meetings2[group]))
        model.Add(penalty_term >= 0)
        penalty_terms.append(penalty_term)

    for group, count in meetings3.items():
        penalty_term = model.NewIntVar(0, num_rounds * 5, f"penalty3_{group}")
        model.Add(penalty_term >= 5 * (count - max(1, fixed_meetings3[group])))
        model.Add(penalty_term >= 0)
        penalty_terms.append(penalty_term)

    for group, count in meetings4.items():
        penalty_term = model.NewIntVar(0, num_rounds * 10, f"penalty4_{group}")
        model.Add(penalty_term >= 10 * (count - max(1, fixed_meetings4[group])))
        model.Add(penalty_term >= 0)
        penalty_terms.append(penalty_term)

    model.Add(penalty == sum(penalty_terms))
    model.Minimize(penalty)

    # Solve the model
    start_time = time.time()
    solution_printer = SolutionPrinter(penalty, start_time)
    print('\nstarting solve')
    status = solver.Solve(model, solution_printer)

    print(f"\nSolver status: {solver.StatusName(status)}")
    print(f"Solving time: {solver.WallTime():.2f} seconds")
    print(f"Optimal penalty: {solver.ObjectiveValue()}")

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No optimal or feasible solution found within the time limit.")
        return None

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
    return seats


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, penalty, start_time):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._penalty = penalty
        self._solution_count = 0

    def on_solution_callback(self):
        current_time = time.time()
        elapsed_time = current_time - self._start_time
        self._solution_count += 1
        print(f'\nSolution {self._solution_count}')
        print(f'  Time = {elapsed_time:.2f} seconds')
        print(f'  Penalty = {self.Value(self._penalty)}')

