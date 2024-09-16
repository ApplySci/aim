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

    return {
        "tables": t_hist,
        "wind": w_hist,
        "meets": meet_hist,
        "indirects": indirect_meet_hist,
    }


def calculate_safe_limits(seats):
    table_count = len(seats[0])
    player_count = table_count * 4
    hanchan_count = len(seats)

    # take square root of player count to get a reasonable minimum for indirect
    #   meetups. Don't worry about indirect meetups for 3 or fewer hanchan
    indirect_min = int(player_count ** 0.5) if hanchan_count >= 4 else 0

    indirect_good = indirect_min + 3
    wind_min = hanchan_count // 4
    wind_max = (hanchan_count + 3) // 4
    table_max = (hanchan_count + table_count * 2 - 1) // table_count
    meetup_max = 1
    return {
        "wind_min": wind_min,
        "wind_max": wind_max,
        "table_max": table_max,
        "indirect_min": indirect_min,
        "indirect_good": indirect_good,
        "meetup_max": meetup_max,
    }


def write_warnings(w_hist, t_hist, meet_hist, indirect_hist,
                   wind_min, wind_max, table_max, indirect_good,
                   meet_max, indirect_min, hanchan_count, table_count,
                   player_count):
    from tabulate import tabulate
    warnings = []
    for n in range(wind_min):
        if w_hist[n] > 0:
            warnings.append(f"Low wind count: {w_hist[n]} occurrence(s) of {n} "
                            " wind allocation(s) for player-wind combinations")

    for n in range(wind_max + 1, hanchan_count + 1):
        if w_hist[n] > 0:
            warnings.append(
                f"High wind count: {w_hist[n]} occurrence(s) of {n} "
                "wind allocations for player-wind combinations")

    for n in range(table_max + 1, hanchan_count + 1):
        if t_hist[n] > 0:
            warnings.append(
                f"High table count: {t_hist[n]} occurrence(s) of {n} "
                "visit(s) to a table by an individual player")

    for n in range(meet_max + 1, hanchan_count + 1):
        if meet_hist[n] > 0:
            warnings.append(
                f"Repeat player meetups: {meet_hist[n]} occurrence(s) of {n} "
                "meetups of the same two players")

    for n in range(0, indirect_min):
        if indirect_hist[n] > 0:
            warnings.append(
                f"Insufficient indirect player meetups: {indirect_hist[n]} "
                f"occurrence(s) of {n} meetups of two players")

    log = '\n==============================================\n'
    if len(warnings) > 0:
        log += f"WARNINGS for {table_count} tables, {hanchan_count} hanchan:\n"
        log += f"{'\n'.join(warnings)}\n"
    else:
        log += f"INFO no warnings for {table_count} tables, {hanchan_count} hanchan\n"

    # table visit frequencies table
    t_hist_table = []
    for i, count in enumerate(t_hist):
        if count > 0:
            t_hist_table.append([i, count])
    log += "\nTable Visit frequencies:\n"
    log += tabulate(t_hist_table, headers=["Table Visits", "Occurrences"], tablefmt="grid")

    # wind frequencies table
    w_hist_table = []
    for i, count in enumerate(w_hist):
        if count > 0:
            w_hist_table.append([i, count])
    log += "\nWind frequencies:\n"
    log += tabulate(w_hist_table, headers=["Wind Count", "Occurrences"], tablefmt="grid")

    # indirect meetup frequencies table
    indirect_hist_table = []
    for i, count in enumerate(indirect_hist):
        if count > 0:
            if i < indirect_good:
                indirect_hist_table.append([i, count])
            elif i == player_count:
                indirect_hist_table.append(['direct', count])
            else:
                indirect_hist_table.append(
                    [f">={indirect_good}", count])

    log += "\nIndirect Meetup frequencies:\n"
    log += tabulate(indirect_hist_table,
                    headers=["Indirect Meetup Count", "Occurrences"],
                    tablefmt="grid")

    return log
