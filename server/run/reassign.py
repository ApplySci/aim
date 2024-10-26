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
    players_to_ignore: list[int] = [0],
) -> int:
    """
    get the stats for a given solution, and return the penalty for it
    """
    stats = make_stats(seats, players_to_ignore)
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


def crossover(genome1, genome2):
    """Perform crossover between two genomes"""
    child = []
    for r in range(len(genome1)):
        if random.random() < 0.5:
            child.append(genome1[r].copy())
        else:
            child.append(genome2[r].copy())
    return child


def mutate(
    genome,
    seats: list[list[list[int]]],
    mutation_rate=0.1,
):
    """Mutate a genome"""
    for r in range(len(genome)):
        if random.random() < mutation_rate:
            # Mutate order
            random.shuffle(genome[r]["order"])

        """  commented out, because this is currently broken
        if random.random() < mutation_rate:
            # Mutate breakups
            if len(genome[r]["breakups"]) > 0:
                if random.random() < 0.5:
                    genome[r]["breakups"].pop(
                        random.randint(0, len(genome[r]["breakups"]) - 1)
                    )
                else:
                    genome[r]["breakups"].append(random.randint(0, len(seats[r]) - 1))
        """
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
    print(f"initial score is {score_solution(seats)}")

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

    # players_to_ignore = list(set([0] + omit_players + substitutes[:direct_subs]))

    # ===================================
    # optimisation starts here
    # ===================================

    population_size = 50
    population = [random_genome(seats, gaps) for _ in range(population_size)]
    best_score = sys.maxsize
    best_genome = None

    while time.time() < end_time:
        # Evaluate fitness
        fitness = []
        for genome in population:
            solution = create_solution(
                [[t.copy() for t in r] for r in seats],
                [g.copy() for g in gaps],
                genome,
            )
            score = score_solution(solution)
            fitness.append((score, genome))

        # Sort by fitness
        fitness.sort(key=lambda x: x[0])

        # Select best individuals
        elite = fitness[: population_size // 2]

        # Create new population
        new_population = [genome for _, genome in elite]

        # introduce some genetic diversity
        for _ in range(population_size // 8):
            new_population.append(random_genome(seats, gaps))
        while len(new_population) < population_size:
            parent1 = random.choice(elite)[1]
            parent2 = random.choice(elite)[1]
            child = crossover(parent1, parent2)
            child = mutate(child, seats)
            new_population.append(child)

        population = new_population

        if fitness[0][0] < best_score:
            best_score = fitness[0][0]
            best_genome = fitness[0][1]

            if verbose:
                print(f"New best score: {best_score}")
        print(".", end="", flush=True)
        sys.stdout.flush()
        if best_score == 0:
            break

    best_solution = create_solution(
        [[t.copy() for t in r] for r in seats],
        [g.copy() for g in gaps],
        best_genome,
    )
    return best_solution
