"""
Seating Statistics Calculator

This module provides functionality to calculate various statistics for
seating arrangements in a tournament or game setting. It analyzes player
distributions across tables, wind positions, direct and indirect meetings,
and repeat encounters.

The main function in this module is:
- make_stats: Calculate statistics for a given seating arrangement

Usage:
    This module is typically imported and used by other modules in the
    seating arrangement analysis system.

Note: This module assumes that players are numbered from 1 to N, where N
is the total number of players, and that there are always 4 players per table.
"""

from typing import List, Dict, Tuple


def make_stats(seats: List[List[List[int]]]) -> Dict[str, List[int]]:
    """
    Calculate statistics for a given seating arrangement.

    Args:
        seats (List[List[List[int]]]): A 3D list representing the seating
            arrangement. The dimensions represent:
            [hanchan][table][seat]

    Returns:
        Dict[str, List[int]]: A dictionary with the following keys:
        - tables: Frequencies of table visits
        - wind: Frequencies of player-wind pairings
        - meets: Frequencies of direct meetings between player pairs
        - indirects: Frequencies of indirect meetings between player pairs
        - repeat3: Count of repeat 3-player meets
        - repeat4: Count of repeat 4-player meets
    """
    table_count = len(seats[0])
    player_count = table_count * 4
    hanchan_count = len(seats)

    player_pairs = [[0 for _ in range(player_count + 1)]
                    for _ in range(player_count + 1)]
    indirect_meets = [[0 for _ in range(player_count + 1)]
                      for _ in range(player_count + 1)]
    player_tables = [[0 for _ in range(table_count)]
                     for _ in range(player_count + 1)]
    player_winds = [[0 for _ in range(4)] for _ in range(player_count + 1)]
    
    # Dictionaries to track 3-player and 4-player meets
    meets3: Dict[Tuple[int, int, int], int] = {}
    meets4: Dict[Tuple[int, int, int, int], int] = {}

    for hanchan in range(hanchan_count):
        for table in range(table_count):
            players_at_table = seats[hanchan][table]
            for seat1 in range(4):
                player1 = players_at_table[seat1]
                player_tables[player1][table] += 1
                player_winds[player1][seat1] += 1
                for seat2 in range(seat1 + 1, 4):
                    player2 = players_at_table[seat2]
                    player_pairs[min(player1, player2)][max(player1, player2)] += 1
            
            # Track 3-player meets
            for i in range(4):
                for j in range(i+1, 4):
                    for k in range(j+1, 4):
                        trio = tuple(sorted([players_at_table[i],
                                             players_at_table[j],
                                             players_at_table[k]]))
                        meets3[trio] = meets3.get(trio, 0) + 1
            
            # Track 4-player meets
            quartet = tuple(sorted(players_at_table))
            meets4[quartet] = meets4.get(quartet, 0) + 1

    for player1 in range(1, player_count + 1):
        for player2 in range(player1 + 1, player_count + 1):
            for player3 in range(1, player_count + 1):
                if (player_pairs[min(player1, player3)][max(player1, player3)] > 0 and
                        player_pairs[min(player2, player3)][max(player2, player3)] > 0):
                    indirect_meets[player1][player2] += 1

    wind_hist = [0] * (hanchan_count + 1)
    table_hist = [0] * (hanchan_count + 1)
    meet_hist = [0] * (hanchan_count + 1)
    indirect_meet_hist = [0] * (player_count + 1)

    for player in range(1, player_count + 1):
        for wind in range(4):
            wind_hist[player_winds[player][wind]] += 1
        for table in range(table_count):
            table_hist[player_tables[player][table]] += 1
        for other_player in range(player + 1, player_count + 1):
            meet_hist[player_pairs[player][other_player]] += 1
            if not player_pairs[player][other_player]:
                indirect_meet_hist[indirect_meets[player][other_player]] += 1

    # Count repeat 3-player and 4-player meets
    repeat3 = sum(1 for count in meets3.values() if count > 1)
    repeat4 = sum(1 for count in meets4.values() if count > 1)
    def truncate_trailing_zeroes(lst):
        while lst and lst[-1] == 0:
            lst.pop()
        return lst

    return {
        "meets": truncate_trailing_zeroes(meet_hist),
        "indirects": truncate_trailing_zeroes(indirect_meet_hist),
        "tables": truncate_trailing_zeroes(table_hist),
        "wind": truncate_trailing_zeroes(wind_hist),
        "repeat3": repeat3,
        "repeat4": repeat4
    }
