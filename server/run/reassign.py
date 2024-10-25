from collections import defaultdict
import random
import sys
import time

from seating.gams.make_stats import make_stats


def create_solution(
    seats: list[list[list[int]]],
    gaps: list[list[int]],
    genome: list[dict[str, list[int]]],
) -> list[list[list[int]]]:
    """
    Create a solution from a genome
    """
    round_count = len(seats)
    # now pick which players to re-seat, to fill the gaps
    for r in range(round_count):
        if len(genome[r]["breakups"]) == 0:
            continue
        reseat = []
        for breakup in genome[r]["breakups"]:
            for s in range(4):
                p = seats[r][breakup][s]
                if p == 0:
                    # remove this from the list of gaps we need to fill
                    gaps[r] = [
                        (t1, s1)
                        for t1, s1 in gaps[r]
                        if not (t1 == breakup and s1 == s)
                    ]
                else:
                    reseat.append(p)
                    seats[r][breakup][s] = 0

        ordered_reseat = [reseat[i] for i in genome[r]["order"] if i < len(reseat)]

        for g in range(len(gaps[r])):
            t, s = gaps[r][g]
            seats[r][t][s] = ordered_reseat[g]

    return seats


def score_solution(
    seats: list[list[list[int]]],
    players_to_ignore: list[int],
) -> int:
    """
    get the stats for a given solution, and return the penalty for it
    """
    stats = make_stats(seats, [0]) # players_to_ignore)
    score = stats["repeat3"] * 10 + stats["repeat4"] * 100
    for i in range(2, len(stats["meets"])):
        score += stats["meets"][i] * (i - 1) ** 2
    return score


def random_genome(
    seats: list[list[list[int]]],
    gaps: list[list[(int, int)]],
) -> list[dict[str, list[int]]]:
    """
    Create a random genome of re-seating
    """
    round_count = len(seats)
    genome = [{} for _ in range(round_count)]
    for r in range(round_count):
        gaps_to_fill = len(gaps[r])
        order = list(range(gaps_to_fill))
        random.shuffle(order)
        genome[r]["order"] = order
        genome[r]["breakups"] = []
        while gaps_to_fill > 0:
            breakup = random.randint(0, len(seats[r]) - 1)
            if breakup in genome[r]:
                continue
            genome[r]["breakups"].append(breakup)
            gaps_to_fill -= 4

    return genome


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

    We will then try different ways to move players between tables,
    to ensure that either a table is all zeros, or it has no zeros.

    We calculate the stats on an outcome to see how good it is

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
    end_time = time.time() + time_limit_seconds
    direct_subs = len(omit_players) % 4
    if direct_subs > len(substitutes):
        raise Exception("Not enough substitutes to fill the gaps")
    round_count = len(seats)
    print(f"initial score is {score_solution(seats, [])}")

    # first remove all omit_players
    gaps = [[] for _ in range(round_count)]
    for r in range(fixed_rounds, round_count):
        for t in range(len(seats[r])):
            for p in range(len(omit_players)):
                if omit_players[p] in seats[r][t]:
                    s = seats[r][t].index(omit_players[p])
                    if p < direct_subs:
                        seats[r][t][s] = substitutes[p]
                    else:
                        seats[r][t][s] = 0
                        gaps[r].append((t, s))

    players_to_ignore = list(set(omit_players + substitutes[:direct_subs]))

    best_score = sys.maxsize
    best_solution = None
    # main optimisation loop will start here
    while time.time() < end_time:
        genome = random_genome(
            seats,
            gaps,
        )
        solution = create_solution(
            [[t.copy() for t in r] for r in seats],
            [g.copy() for g in gaps],
            genome,
        )
        score = score_solution(
            solution,
            players_to_ignore,
        )
        if score < best_score:
            best_score = score
            best_solution = solution
            if verbose:
                print(f"New best score: {best_score}")

    return best_solution
