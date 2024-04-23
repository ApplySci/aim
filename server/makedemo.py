'''
this is all proof-of-concept stuff
It doesn't actually do anything useful yet
But it is helping me learn how to do these things
'''

import json
import datetime
from pathlib import Path

from firebase_admin import credentials, initialize_app as fcm_init
from firebase_admin import firestore

basedir = Path('/home/model/src/tournaments-static/')
# basedir = Path('D:\\zaps\\aim_tournaments\\server')

demoTournament = 'Y3sDqxajiXefmP9XBTvY'

# Use the private key file of the service account directly.
cred = credentials.Certificate("fcm-admin.json")
app = fcm_init(cred)
firestore_client = firestore.client()

ref = firestore_client.collection("tournaments")
print(ref.document(demoTournament).get().to_dict())


def get_tourney_json():
    seating = [
        {   'id': 'R1',
            'start': 'Saturday 09.00',
            'tables': {
                'alef': [1, 2, 3, 4],
                'bet': [5, 6, 7, 8],
                'gimel': [9, 10, 11, 12],
                'dalet': [13, 14, 15, 16],
                'he': [17, 18, 19, 20],
            },
        },
        {   'id': 'R2',
            'start': 'Saturday 11.00',
            'tables': {
                'alef': [2, 4, 6, 8],
                'bet': [1, 3, 5, 7],
                'gimel': [10, 14, 16, 20],
                'dalet': [9, 11, 13, 15],
                'he': [12, 17, 18, 19],
            },
        },
        {   'id': 'R3',
            'start': 'Saturday 14.00',
            'tables': {
                'alef': [1, 7, 14, 20],
                'bet': [2, 6, 13, 19],
                'gimel': [3, 5, 12, 18],
                'dalet': [4, 16, 9, 8],
                'he': [17, 10, 11, 15],
            },
        }
    ]

    scores = [
        {
            'id': 1,
            't': 50,
            's': [0, -24, 49, 91, -11, -30]
        },
        {
            'id': 2,
            't': 200,
            's': [0, 15, 23, 35, 53, 112]
        },
        {
            'id': 3,
            't': -105,
            's': [0, 0, -40, 5, -36, -69]
        },
        {
            'id': 4,
            't': -145,
            's': [0, 10, 12, -126, -6, -13]
        },
        {
            'id': 5,
            't': 50,
            's': [0, -24, 49, 91, -11, -30]
        },
        {
            'id': 6,
            't': 200,
            's': [0, 15, 23, 35, 53, 112]
        },
        {
            'id': 7,
            't': -100,
            's': [0, 0, -40, 5, -36, -69]
        },
        {
            'id': 8,
            't': -140,
            's': [0, 10, 12, -126, -6, -13]
        },
        {
            'id': 9,
            't': 52,
            's': [0, -24, 49, 91, -11, -30]
        },
        {
            'id': 10,
            't': 186,
            's': [0, 15, 23, 35, 53, 112]
        },
        {
            'id': 11,
            't': -108,
            's': [0, 0, -40, 5, -36, -69]
        },
        {
            'id': 12,
            't': -101,
            's': [0, 10, 12, -126, -6, -13]
        },
        {
            'id': 13,
            't': 67,
            's': [0, -24, 49, 91, -11, -30]
        },
        {
            'id': 14,
            't': 808,
            's': [0, 15, 23, 35, 53, 112]
        },
        {
            'id': 15,
            't': -909,
            's': [0, 0, -40, 5, -36, -69]
        },
        {
            'id': 16,
            't': -707,
            's': [0, 10, 12, -126, -6, -13]
        },
        {
            'id': 17,
            't': 606,
            's': [0, -24, 49, 91, -11, -30]
        },
        {
            'id': 18,
            't': 505,
            's': [0, 15, 23, 35, 53, 112]
        },
        {
            'id': 19,
            't': 404,
            's': [0, 0, -40, 5, -36, -69]
        },
        {
            'id': 20,
            't': -303,
            's': [0, 10, 12, -126, -6, -13]
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

    sorted_scores = sorted(scores, key=lambda r: -r['t'])
    rank = 0
    row_number = 1
    previous_score = -99999.9
    for row in sorted_scores:
        if previous_score == row['t']:
            prefix = '='
        else:
            previous_score = row['t']
            rank = row_number
            prefix = ''

        row['r'] = f'{prefix}{rank}'
        row_number += 1

    sorted_scores[0]['roundDone'] = 1

    return (players, seating, sorted_scores)


# write_files()

def write_cloudstore():
    players, seating, sorted_scores = get_tourney_json()
    pj  = json.dumps(players,       ensure_ascii=False, indent=None)
    sj  = json.dumps(seating,       ensure_ascii=False, indent=None)
    ssj = json.dumps(sorted_scores, ensure_ascii=False, indent=None)

    ref.document(f"{demoTournament}/json/players").set(document_data={
        'json': pj})
    ref.document(f"{demoTournament}/json/seating").set(document_data={
        'json': sj})
    ref.document(f"{demoTournament}/json/scores").set(document_data={
        'json': ssj})

write_cloudstore()
