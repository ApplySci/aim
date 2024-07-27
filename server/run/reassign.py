from collections import defaultdict
import random

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
            player for player in seats[round_idx][table_to_remove]
            if player not in dropouts_set
        ]
        for group_idx, group in enumerate(seats[round_idx]):
            if group_idx != table_to_remove:
                new_group = [
                    player for player in group if player not in dropouts_set
                ]
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
                for player2 in group[i+1:]:
                    meet_counts[player1][player2] += 1
                    meet_counts[player2][player1] += 1
                    meet_rounds[player1][player2].append(round_idx + 1)
                    meet_rounds[player2][player1].append(round_idx + 1)

    # Whenever that number is greater than 1, list the two players and the rounds they meet.
    print('*** collisions:')
    for player1, opponents in meet_counts.items():
        for player2, count in opponents.items():
            if count > 1:
                rounds_met = meet_rounds[player1][player2]
                print(f"Players {player1} and {player2} meet {count} times in rounds {rounds_met}")
    print('*** end of collisions:')

    return new_seats



if __name__ == "__main__":
    from seating.seats_48x7 import seats
    dropouts = [1, 2, 3, 4]
    new_seats = reassign_groups(seats, dropouts)
    for round_idx, round in enumerate(new_seats):
        print(f"Round {round_idx + 1}:")
        for group in round:
            print(group)