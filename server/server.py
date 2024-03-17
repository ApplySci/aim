import json
import datetime
from pathlib import Path

from firebase_admin import credentials, messaging as fcm, \
    initialize_app as fcm_init

cred = credentials.Certificate("fcm-admin.json")
default_app = fcm_init(cred)

basedir = Path('/home/model/src/tournaments-static/')
# basedir = Path('d:/zaps/')

TOKEN = 'eu3cnQqXT9KsekF0nUuH10:APA91bFbXIjd_ymM9b2ddXDmEoUB1NTzli3eHSo2lNfimkp8QvthA-QZf24BHi8LB6RuejxtkkWewnb3wDr5nyHynz7-3TP9ZyikRRFakdrfh41T_HmMnNn9--sihcPYbEL3i-JZ-f6H'

def send_notification():

    # See documentation on defining a message payload.
    message = fcm.Message(token=TOKEN,
        notification=fcm.Notification(title='Seating', body='just updated'),
        data={'type': 'seats',},
        android=fcm.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=fcm.AndroidNotification(
                channel_id='aim112',
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
    )

    response = fcm.send(message)
    # message ID
    print('Response to sent message:', response)

# =================================================================

# https://firebase.google.com/docs/cloud-messaging/send-message

# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modified by AZPS

def send_to_token():
    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.
    registration_token = 'YOUR_REGISTRATION_TOKEN'

    # See documentation on defining a message payload.
    message = fcm.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = fcm.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_token]


def send_to_topic():
    # [START send_to_topic]
    # The topic name can be optionally prefixed with "/topics/".
    topic = 'highScores'

    # See documentation on defining a message payload.
    message = fcm.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        topic=topic,
    )

    # Send a message to the devices subscribed to the provided topic.
    response = fcm.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_topic]


def send_to_condition():
    # [START send_to_condition]
    # Define a condition which will send to devices which are subscribed
    # to either the Google stock or the tech industry topics.
    condition = "'stock-GOOG' in topics || 'industry-tech' in topics"

    # See documentation on defining a message payload.
    message = fcm.Message(
        notification=fcm.Notification(
            title='$GOOG up 1.43% on the day',
            body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        ),
        condition=condition,
    )

    # Send a message to devices subscribed to the combination of topics
    # specified by the provided condition.
    response = fcm.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_condition]


def send_dry_run():
    message = fcm.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token='token',
    )

    # [START send_dry_run]
    # Send a message in the dry run mode.
    response = fcm.send(message, dry_run=True)
    # Response is a message ID string.
    print('Dry run successful:', response)
    # [END send_dry_run]


def android_message():
    # [START android_message]
    message = fcm.Message(
        android=fcm.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=fcm.AndroidNotification(
                title='$GOOG up 1.43% on the day',
                body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
        topic='industry-tech',
    )
    # [END android_message]
    return message


def apns_message():
    # [START apns_message]
    message = fcm.Message(
        apns=fcm.APNSConfig(
            headers={'apns-priority': '10'},
            payload=fcm.APNSPayload(
                aps=fcm.Aps(
                    alert=fcm.ApsAlert(
                        title='$GOOG up 1.43% on the day',
                        body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
                    ),
                    badge=42,
                ),
            ),
        ),
        topic='industry-tech',
    )
    # [END apns_message]
    return message


def webpush_message():
    # [START webpush_message]
    message = fcm.Message(
        webpush=fcm.WebpushConfig(
            notification=fcm.WebpushNotification(
                title='$GOOG up 1.43% on the day',
                body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
                icon='https://my-server/icon.png',
            ),
        ),
        topic='industry-tech',
    )
    # [END webpush_message]
    return message


def all_platforms_message():
    # [START multi_platforms_message]
    message = fcm.Message(
        notification=fcm.Notification(
            title='$GOOG up 1.43% on the day',
            body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        ),
        android=fcm.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=fcm.AndroidNotification(
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
        apns=fcm.APNSConfig(
            payload=fcm.APNSPayload(
                aps=fcm.Aps(badge=42),
            ),
        ),
        topic='industry-tech',
    )
    # [END multi_platforms_message]
    return message


def subscribe_to_topic():
    topic = 'highScores'
    # [START subscribe]
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_n',
    ]

    # Subscribe the devices corresponding to the registration tokens to the
    # topic.
    response = fcm.subscribe_to_topic(registration_tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, 'tokens were subscribed successfully')
    # [END subscribe]


def unsubscribe_from_topic():
    topic = 'highScores'
    # [START unsubscribe]
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_n',
    ]

    # Unubscribe the devices corresponding to the registration tokens from the
    # topic.
    response = fcm.unsubscribe_from_topic(registration_tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, 'tokens were unsubscribed successfully')
    # [END unsubscribe]


def send_all():
    registration_token = 'YOUR_REGISTRATION_TOKEN'
    # [START send_all]
    # Create a list containing up to 500 messages.
    messages = [
        fcm.Message(
            notification=fcm.Notification('Price drop', '5% off all electronics'),
            token=registration_token,
        ),
        # ...
        fcm.Message(
            notification=fcm.Notification('Price drop', '2% off all books'),
            topic='readers-club',
        ),
    ]

    response = fcm.send_all(messages)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print('{0} messages were sent successfully'.format(response.success_count))
    # [END send_all]


def send_multicast():
    # [START send_multicast]
    # Create a list containing up to 500 registration tokens.
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_N',
    ]

    message = fcm.MulticastMessage(
        data={'score': '850', 'time': '2:45'},
        tokens=registration_tokens,
    )
    response = fcm.send_multicast(message)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print('{0} messages were sent successfully'.format(response.success_count))
    # [END send_multicast]


def send_multicast_and_handle_errors():
    # [START send_multicast_error]
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_N',
    ]

    message = fcm.MulticastMessage(
        data={'score': '850', 'time': '2:45'},
        tokens=registration_tokens,
    )
    response = fcm.send_multicast(message)
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(registration_tokens[idx])
        print('List of tokens that caused failures: {0}'.format(failed_tokens))
    # [END send_multicast_error]



# END OF GOOGLE COPYRIGHTED SECTION

# =====================================================================

def write_files():
    seating = [
        {   'id': 'R1',
            'roundDone': 1,
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

write_files()
