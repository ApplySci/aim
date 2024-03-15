import json
from pathlib import Path

basedir = Path('/home/model/apps/tournaments/myapp/data/')
# basedir = Path('d:/zaps/aim_tournaments/')

seating = {
    'R1': {
        'start': 'Saturday 09.00',
        'tables': {
            'alef': [1, 2, 3, 4],
            'bet': [5, 6, 7, 8],
        },
    },
    'R2': {
        'start': 'Saturday 11.00',
        'tables': {
            'alef': [2, 4, 6, 8],
            'bet': [1, 3, 5, 7],
        },
    },
    'R3': {
        'start': 'Saturday 14.00',
        'tables': {
            'alef': [3, 4, 1, 6],
            'bet': [2, 7, 8, 5],
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
        'total': -105,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 8,
        'total': -145,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
    {
        'id': 9,
        'total': 50,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 10,
        'total': 200,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 11,
        'total': -105,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 12,
        'total': -145,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
    {
        'id': 13,
        'total': 50,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 14,
        'total': 200,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 15,
        'total': -105,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 16,
        'total': -145,
        'roundScores': [0, 10, 12, -126, -6, -13]
    },
    {
        'id': 17,
        'total': 50,
        'roundScores': [0, -24, 49, 91, -11, -30]
    },
    {
        'id': 18,
        'total': 200,
        'roundScores': [0, 15, 23, 35, 53, 112]
    },
    {
        'id': 19,
        'total': -105,
        'roundScores': [0, 0, -40, 5, -36, -69]
    },
    {
        'id': 20,
        'total': -145,
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

with open(basedir / 'players.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, ensure_ascii=False, indent=0)

with open(basedir / 'seating.json', 'w', encoding='utf-8') as f:
    json.dump(seating, f, ensure_ascii=False, indent=0)

with open(basedir / 'scores.json', 'w', encoding='utf-8') as f:
    json.dump(scores, f, ensure_ascii=False, indent=0)
