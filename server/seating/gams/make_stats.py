# -*- coding: utf-8 -*-

def make_stats(seats):
    """
    returns a dict with the following keys:
    - tables: a list of frequencies of table visits
    - wind: a list of frequencies of player-wind pairings
    - meets: a list of frequencies of the number of times each pair of players meet directly
    - indirects: a list of frequencies of the number of times each pair of players meet indirectly
    - repeat3: count of repeat 3-player meets
    - repeat4: count of repeat 4-player meets
    """
    table_count = len(seats[0])
    player_count = table_count * 4
    hanchan_count = len(seats)

    p_p = [[0 for _ in range(player_count + 1)] for _ in range(player_count + 1)]
    ppp = [[0 for _ in range(player_count + 1)] for _ in range(player_count + 1)]
    p_t = [[0 for _ in range(table_count)] for _ in range(player_count + 1)]
    p_wind = [[0 for _ in range(4)] for _ in range(player_count + 1)]
    
    # New dictionaries to track 3-player and 4-player meets
    meets3 = {}
    meets4 = {}

    for h in range(hanchan_count):
        for t in range(table_count):
            players_at_table = seats[h][t]
            for s1 in range(0, 4):
                p1 = players_at_table[s1]
                p_t[p1][t] += 1
                p_wind[p1][s1] += 1
                for s2 in range(s1 + 1, 4):
                    p2 = players_at_table[s2]
                    p_p[min(p1, p2)][max(p1, p2)] += 1
            
            # Track 3-player meets
            for i in range(4):
                for j in range(i+1, 4):
                    for k in range(j+1, 4):
                        trio = tuple(sorted([players_at_table[i], players_at_table[j], players_at_table[k]]))
                        meets3[trio] = meets3.get(trio, 0) + 1
            
            # Track 4-player meets
            quartet = tuple(sorted(players_at_table))
            meets4[quartet] = meets4.get(quartet, 0) + 1

    for p1 in range(1, player_count + 1):
        for p2 in range(p1 + 1, player_count + 1):
            for p3 in range(1, player_count + 1):
                if p_p[min(p1, p3)][max(p1, p3)] > 0 and \
                        p_p[min(p2, p3)][max(p2, p3)] > 0:
                    ppp[p1][p2] += 1
            ppp[p1][p2] += p_p[p1][p2] * player_count

    w_hist = [0] * (hanchan_count + 1)
    t_hist = [0] * (hanchan_count + 1)
    meet_hist = [0] * (hanchan_count + 1)
    indirect_meet_hist = [0] * (player_count + 1)

    for p1 in range(1, player_count + 1):
        for s in range(4):
            w_hist[p_wind[p1][s]] += 1
        for t in range(table_count):
            t_hist[p_t[p1][t]] += 1
        for p2 in range(p1 + 1, player_count + 1):
            meet_hist[p_p[p1][p2]] += 1
            indirect_meet_hist[
                min(ppp[p1][p2], player_count)
                ] += 1

    # Count repeat 3-player and 4-player meets
    repeat3 = sum(1 for count in meets3.values() if count > 1)
    repeat4 = sum(1 for count in meets4.values() if count > 1)

    return {
        "meets": meet_hist,
        "indirects": indirect_meet_hist,
        "tables": t_hist,
        "wind": w_hist,
        "repeat3": repeat3,
        "repeat4": repeat4
    }
