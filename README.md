# aim

[All-Ireland Mahjong](https://mahjong.ie/) mobile app.
This will provide information about upcoming tournaments.

The client-side written in Flutter for android (tested), and is built in Android Studio.
 It will hopefully work in IOS too, but this has not yet been tested.

Server-side written in Python. App notifications are by Firebase Cloud Messaging
(via APN, for IOS)

For tournament participants, it will give **live** info during tournament: current scores,
which table a given player is on next and when the round starts, etc

Push notifications will let players know when the latest scores are available, and these scores will
appear in the app. Players will also receive notifications if the timing or seating plans have
changed.

# Coding decisions that might be unexpected:

### Scores stored as integers

Scores are multiplied by 10 and stored as integers. To avoid any nonsense with inaccurate
floating point arithmetic.
So a tournament score of +29.1 is stored as 291. A score of -5.0 is stored as -50.
Scores are expected to be received from the server in this form too.

The **only** place
where the conversion is done back to decimal, in the app, is at the final point of display. This
happens in [lib/score_cell.dart](lib/score_cell.dart#L16)


### All state is in a single global variable

All of the state is stored in a single global state variable, of class AllState. I have no idea
as to whether that's a good way or a bad way to do it. [lib/store.dart](lib/store.dart#L53)

### There's no login.

All info is public. This bypasses any issues around privacy policies, age requirements, etc.
