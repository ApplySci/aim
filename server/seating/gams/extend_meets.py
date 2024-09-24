"""
Seating Arrangement Extension Module

This module provides functionality to extend seating arrangements for
tournaments or games with a larger number of rounds (hanchans) than the
original arrangement.

The main function in this module is:
- extend_meets: Extend a seating arrangement to cover more rounds

Usage:
    This module can be run directly to extend a seating arrangement,
    or imported and used by other modules in the seating arrangement system.

Note: This module assumes the existence of seating arrangement modules
in the 'sgp' package, named according to the number of players.
"""

import random
import time
import importlib
import os
from typing import List, Tuple, Dict


def calculate_penalty(seating: List[List[List[int]]]) -> int:
    """
    Calculate the penalty score for a given seating arrangement.

    The penalty is based on repeated meetings between groups of 3 and 4 players.

    Args:
        seating (List[List[List[int]]]): A 3D list representing the seating
            arrangement. The dimensions represent: [hanchan][table][seat]

    Returns:
        int: The calculated penalty score
    """
    penalty = 0
    player_count = max(max(table) for hanchan in seating for table in hanchan)
    
    # Count meetings for groups of 3 and 4 players
    meetings3 = {tuple(sorted([p1, p2, p3])): 0 for p1 in range(1, player_count+1) 
                 for p2 in range(p1+1, player_count+1) 
                 for p3 in range(p2+1, player_count+1)}
    meetings4 = {tuple(sorted([p1, p2, p3, p4])): 0 for p1 in range(1, player_count+1) 
                 for p2 in range(p1+1, player_count+1) 
                 for p3 in range(p2+1, player_count+1)
                 for p4 in range(p3+1, player_count+1)}

    for hanchan in seating:
        for table in hanchan:
            for i in range(len(table)):
                for j in range(i+1, len(table)):
                    for k in range(j+1, len(table)):
                        meetings3[tuple(sorted([table[i], table[j], table[k]]))] += 1
            if len(table) == 4:
                meetings4[tuple(sorted(table))] += 1

    # Calculate penalty
    for group, count in meetings3.items():
        if count > 1:
            penalty += count - 1
    for group, count in meetings4.items():
        if count > 1:
            penalty += 10 * (count - 1)

    return penalty


def extend_meets(player_count: int, hanchan_count: int, time_limit: int = 600) -> List[List[List[int]]]:
    """
    Extend a seating arrangement to cover more rounds (hanchans).

    Args:
        player_count (int): The number of players
        hanchan_count (int): The desired number of rounds (hanchans)
        time_limit (int, optional): Time limit for optimization in seconds. Defaults to 600.

    Returns:
        List[List[List[int]]]: The extended seating arrangement
    """
    # Import original seating arrangement
    module_name = f"sgp.{player_count}"
    original_seats = importlib.import_module(module_name).seats
    
    original_hanchan_count = len(original_seats)
    additional_hanchan_count = hanchan_count - original_hanchan_count
    
    if additional_hanchan_count <= 0:
        return original_seats

    best_seating = original_seats + original_seats[:additional_hanchan_count]
    best_penalty = calculate_penalty(best_seating)

    start_time = time.time()
    iterations = 0

    while time.time() - start_time < time_limit:
        # Create a random 1-to-1 mapping
        player_mapping = list(range(1, player_count + 1))
        random.shuffle(player_mapping)
        mapping = {i+1: player_mapping[i] for i in range(player_count)}

        # Apply the mapping to create new seating arrangement
        new_seating = original_seats.copy()
        for i in range(additional_hanchan_count):
            mapped_hanchan = []
            for table in original_seats[i % original_hanchan_count]:
                mapped_table = [mapping[player] for player in table]
                mapped_hanchan.append(mapped_table)
            new_seating.append(mapped_hanchan)

        new_penalty = calculate_penalty(new_seating)

        if new_penalty < best_penalty:
            print(f"Iteration {iterations}; new penalty: {new_penalty}")
            best_seating = new_seating
            best_penalty = new_penalty
            if new_penalty == 0:
                break

        iterations += 1

    print(f"Best penalty: {best_penalty}")
    print(f"Iterations: {iterations}")

    return best_seating


def save_extended_seating(player_count: int, hanchan_count: int, seating: List[List[List[int]]]) -> None:
    """
    Save the extended seating arrangement to a file.

    Args:
        player_count (int): The number of players
        hanchan_count (int): The number of rounds (hanchans)
        seating (List[List[List[int]]]): The seating arrangement to save

    Returns:
        None
    """
    os.makedirs("meets", exist_ok=True)
    output_file = f"meets/{player_count}x{hanchan_count}.py"
    with open(output_file, "w") as f:
        out = f"{seating}\n".replace("],", "],\n")
        f.write(f"seats = {out}\n")
    print(f"Extended seating arrangement saved to {output_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python extend_meets.py <player_count> <hanchan_count>")
        sys.exit(1)
    
    player_count = int(sys.argv[1])
    hanchan_count = int(sys.argv[2])
    
    result = extend_meets(player_count, hanchan_count)
    
    # Import original seating arrangement to get the original hanchan count
    module_name = f"sgp.{player_count}"
    original_seats = importlib.import_module(module_name).seats
    original_hanchan_count = len(original_seats)

    # Write results for each intermediate hanchan count
    for i in range(original_hanchan_count + 1, hanchan_count + 1):
        save_extended_seating(player_count, i, result[:i])
