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

    # TODO optimisation here, with time limit time_limit_seconds
    # len(seats[r][t]) is always 4, for all r,t
    # seats[r][t].count(0) must be either 0 or 4, for any r,t

    # finally, return the new seating arrangement
    return seats


def social_golfer_problem_with_time_limit(
    weeks,
    groups_per_week,
    players_per_group,
    num_players,
    time_limit_seconds,
):
    model = cp_model.CpModel()

    # Create variables (same as before)
    plays = {}
    for w in range(weeks):
        for g in range(groups_per_week):
            for p in range(num_players):
                plays[w, g, p] = model.NewBoolVar(f"w{w}g{g}p{p}")

    # Basic constraints (same as before)
    for w in range(weeks):
        for p in range(num_players):
            model.Add(sum(plays[w, g, p] for g in range(groups_per_week)) == 1)

    for w in range(weeks):
        for g in range(groups_per_week):
            model.Add(
                sum(plays[w, g, p] for p in range(num_players)) == players_per_group
            )

    # No two players play together more than once (with slack)
    slack_vars = []
    for p1 in range(num_players):
        for p2 in range(p1 + 1, num_players):
            slack = model.NewIntVar(0, weeks, f"slack_{p1}_{p2}")
            model.Add(
                sum(
                    plays[w, g, p1] * plays[w, g, p2]
                    for w in range(weeks)
                    for g in range(groups_per_week)
                )
                <= 1 + slack
            )
            slack_vars.append(slack)

    # Objective: Minimize the sum of slack variables
    model.Minimize(sum(slack_vars))

    # Solve the model with time limit
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds

    solution_printer = SolutionPrinter(plays, weeks, groups_per_week, num_players)
    status = solver.SolveWithSolutionCallback(model, solution_printer)

    # Print final solution and statistics
    print(f"Final status: {solver.StatusName(status)}")
    print(f"Objective value: {solver.ObjectiveValue()}")
    print(f"Solve time: {solver.WallTime()} seconds")

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        solution_printer.print_solution(solver)
    else:
        print("No solution found within the time limit.")


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, plays, weeks, groups_per_week, num_players):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._plays = plays
        self._weeks = weeks
        self._groups_per_week = groups_per_week
        self._num_players = num_players
        self._solution_count = 0
        self._start_time = time.time()

    def on_solution_callback(self):
        current_time = time.time()
        print(
            f"\nSolution {self._solution_count + 1} (at {current_time - self._start_time:.2f} seconds):"
        )
        print(f"Objective value: {self.ObjectiveValue()}")
        self._solution_count += 1
        self.print_solution(self)

    def print_solution(self, solver):
        for w in range(self._weeks):
            print(f"Week {w + 1}:")
            for g in range(self._groups_per_week):
                group = [
                    p
                    for p in range(self._num_players)
                    if solver.Value(self._plays[w, g, p])
                ]
                print(f"  Group {g + 1}: {group}")


# Example usage
social_golfer_problem_with_time_limit(
    weeks=3,
    groups_per_week=2,
    players_per_group=2,
    num_players=6,
    time_limit_seconds=10,
)


def reassign_groups(seats, dropouts):
    # Create a set of dropouts for quick lookup
    dropouts_set = set(dropouts)

    # Create a dictionary to track the groups of each player in rounds 1-4
    player_groups = defaultdict(list)
    for round_idx in range(4):
        for group_idx, group in enumerate(seats[round_idx]):
            for player in group:
                player_groups[player].append((round_idx, group_idx))

    # Create a new seating arrangement for rounds 5-7
    new_seats = seats[:4]  # Keep the first 4 rounds unchanged
    for round_idx in range(4, 7):
        new_round = []
        dropout_counts = []
        for group in seats[round_idx]:
            dropout_count = sum(player in dropouts_set for player in group)
            dropout_counts.append(dropout_count)

        # Find the table with the most dropouts
        max_dropouts = max(dropout_counts)
        tables_with_max_dropouts = [
            i for i, count in enumerate(dropout_counts) if count == max_dropouts
        ]
        table_to_remove = random.choice(tables_with_max_dropouts)

        # Reassign players from the removed table
        removed_players = [
            player
            for player in seats[round_idx][table_to_remove]
            if player not in dropouts_set
        ]
        for group_idx, group in enumerate(seats[round_idx]):
            if group_idx != table_to_remove:
                new_group = [player for player in group if player not in dropouts_set]
                while len(new_group) < 4 and removed_players:
                    new_group.append(removed_players.pop(0))
                new_round.append(new_group)

        # If there are still players left to reassign, distribute them to the groups
        # with less than 4 players
        for player in removed_players:
            for group in new_round:
                if len(group) < 4:
                    group.append(player)
                    break

        new_seats.append(new_round)

    # Count how many times each player meets each other player across all rounds.
    meet_counts = defaultdict(lambda: defaultdict(int))
    meet_rounds = defaultdict(lambda: defaultdict(list))

    for round_idx, round in enumerate(new_seats):
        for group in round:
            for i, player1 in enumerate(group):
                for player2 in group[i + 1 :]:
                    meet_counts[player1][player2] += 1
                    meet_counts[player2][player1] += 1
                    meet_rounds[player1][player2].append(round_idx + 1)
                    meet_rounds[player2][player1].append(round_idx + 1)

    # Whenever that number is greater than 1, list the two players and the rounds they meet.
    print("*** collisions:")
    for player1, opponents in meet_counts.items():
        for player2, count in opponents.items():
            if count > 1:
                rounds_met = meet_rounds[player1][player2]
                print(
                    f"Players {player1} and {player2} meet {count} times in rounds {rounds_met}"
                )
    print("*** end of collisions:")

    return new_seats


if __name__ == "__main__":
    from seating.seats_7 import original_seats  # 7 hanchan

    seats = original_seats[7]  # 28 players
    dropouts = [1, 5, 15, 23]
    new_seats = reassign_groups(seats, dropouts, fixed=4)
    for round_idx, round in enumerate(new_seats):
        print(f"Round {round_idx + 1}:")
        for group in round:
            print(group)
