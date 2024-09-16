# -*- coding: utf-8 -*-

def make_stats(seats):
    """
    returns a dict with the following keys:
    - tables: a list of frequencies of table visits
    - wind: a list of frequencies of player-wind pairings
    - meets: a list of frequencies of the number of times each pair of players meet directly
    - indirects: a list of frequencies of the number of times each pair of players meet indirectly
    """
    table_count = len(seats[0])
    player_count = table_count * 4
    hanchan_count = len(seats)

    p_p = [[0 for _ in range(player_count + 1)] for _ in range(player_count + 1)]
    ppp = [[0 for _ in range(player_count + 1)] for _ in range(player_count + 1)]
    p_t = [[0 for _ in range(table_count)] for _ in range(player_count + 1)]
    p_wind = [[0 for _ in range(4)] for _ in range(player_count + 1)]

    for h in range(hanchan_count):
        for t in range(table_count):
            for s1 in range(0, 4):
                p1 = seats[h][t][s1]
                p_t[p1][t] += 1
                p_wind[p1][s1] += 1
                for s2 in range(s1 + 1, 4):
                    p2 = seats[h][t][s2]
                    p_p[min(p1, p2)][max(p1, p2)] += 1

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

    return meet_hist, indirect_meet_hist, t_hist, w_hist
