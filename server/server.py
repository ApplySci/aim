import json
from pathlib import Path

# basedir = Path('/home/model/src/tournaments-static/')
basedir = Path('d:/zaps/')

seating = { # TODO more tables
    'R1': {
        'start': 'Saturday 09.00',
        'tables': {
            'alef': [1, 2, 3, 4],
            'bet': [5, 6, 7, 8],
            'gimel': [9, 10, 11, 12],
            'dalet': [13, 14, 15, 16],
            'he': [17, 18, 19, 20],
        },
    },
    'R2': {
        'start': 'Saturday 11.00',
        'tables': {
            'alef': [2, 4, 6, 8],
            'bet': [1, 3, 5, 7],
            'gimel': [10, 14, 16, 20],
            'dalet': [9, 11, 13, 15],
            'he': [12, 17, 18, 19],
        },
    },
    'R3': {
        'start': 'Saturday 14.00',
        'tables': {
            'alef': [1, 7, 14, 20],
            'bet': [2, 6, 13, 19],
            'gimel': [3, 5, 12, 18],
            'dalet': [4, 16, 9, 8],
            'he': [17, 10, 11, 15],
        },
    }
}

scores = [
    {
        'id': 1,
        'total': 50,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 2,
        'total': 200,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 3,
        'total': -105,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 4,
        'total': -145,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
    {
        'id': 5,
        'total': 50,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 6,
        'total': 200,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 7,
        'total': -100,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 8,
        'total': -140,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
    {
        'id': 9,
        'total': 52,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 10,
        'total': 186,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 11,
        'total': -108,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 12,
        'total': -101,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
    {
        'id': 13,
        'total': 67,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 14,
        'total': 808,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 15,
        'total': -909,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 16,
        'total': -707,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
    {
        'id': 17,
        'total': 606,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 18,
        'total': 505,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 19,
        'total': 404,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 20,
        'total': -303,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
]

players = {
    3: 'Aphra Behn',
    2: 'Barbara of Cilli',
    1: 'Clara Schumann',
    4: 'Dorath Pinto Uchôa',
    5: 'Elinor Ostrom',
    6: 'Frida Kahlo',
    7: 'Grace Jones',
    8: 'Hedy Lamarr',
    9: 'Isabel Allende',
    10: 'Jocelyn Bell Burnell',
    11: 'Katharine Hayhoe',
    12: 'Lucy Liu',
    13: 'Mary Seacole',
    14: 'Natalie Merchant',
    15: 'Ольга Александровна Ладыженская',
    16: 'Phumzile Mlambo-Ngcuka',
    17: 'Queen Nefertiti',
    18: 'Rachel Carson',
    19: '松原 幸子',
    20: '津田 梅子'
}

sorted_scores = sorted(scores, key=lambda r: -r['total'])
rank = 0
row_number = 1
previous_score = -99999.9
for row in sorted_scores:
    if previous_score == row['total']:
        prefix = '='
    else:
        previous_score = row['total']
        rank = row_number
        prefix = ''

    row['rank'] = f'{prefix}{rank}'
    row_number += 1

with open(basedir / 'players.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, ensure_ascii=False, indent=0)

with open(basedir / 'seating.json', 'w', encoding='utf-8') as f:
    json.dump(seating, f, ensure_ascii=False, indent=0)

with open(basedir / 'scores.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_scores, f, ensure_ascii=False, indent=0)
