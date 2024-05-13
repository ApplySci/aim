# aim

[All-Ireland Mahjong](https://mahjong.ie/) mobile app.
This provides live information about tournaments.

For tournament participants, it gives **live** info during tournament: current scores,
which table a given player is on next and when the round starts, etc

Push notifications will let players know when the latest scores are available, and these scores will
appear in the app. Players will also receive notifications if the timing or seating plans
change, as soon as they change. An app user can choose to get information about any one
specific player, and the expectation is that a player will choose to get information about
themselves (but there are no constraints on this). If they do, then they'll receive tailored
information about which table they are on next, and who they'll be playing with.
And they'll get tailored notifications if that information changes.

A tournament admin will be able to do everything through a web interface.
I envisage them using 3 browser tabs:

- the admin interface
- the google scoring sheet; and
- the live web page; and

## Programming platforms, frameworks & languages used

The client-side written in Dart with the **Flutter** framework. It's developed and
tested initially for **android**, in Android Studio.
The intention is that it will work on **iPhone** too (not started yet), which is why I chose
Flutter, because it works across platforms. But there's still some platform-specific
configuration to do.

The server-side is written in **Python**, with the **Flask** framework. I'm running it
on the server with **wsgi**. Note that the oauth2 authentication won't work on localhost: you need
a google project that knows about the domain that the app is being served from, and must be given
the post-authentication URL to redirect back to.  **GSPRead** is used to read the
scoresheet, to create the live score web page, and to put the data into the
cloud, for onward transmission to the app

App notifications are by **Firebase Cloud Messaging**.
And via **APN**, for IOS (not started yet).
Live tournament data is stored in **Google Cloud Firestore**.

When the app has a connection, and is in foreground or background, any update to
the firebase cloud data gets noticed by the listener.
If the app is closed, then it won't know anything about it, so the server sends FCM notificaions
to all subscribed devices.

The live scoring of a tournament is done in a **Google spreadsheet**,
based on the one developed by David Bresnick for the World Riichi Championship.

## Coding decisions that might be unexpected (and might be unsound):

### Going via firebase cloud store for the data, rather than server -> app directly

I've had a few trial run-ups at it, and after a few false starts, have settled on
google firebase & cloud messaging because it will be free for the level of use I'm anticipating,
and because it takes care of loads of messy stuff such as background syncing of
data between mobiles and server, and caching stuff on mobile so that everything
behaves just perfectly even when the mobile has patchy signal. I did try crafting my own
local caching thing for android, and it was super messy, so it just made sense to let google
do all the clever io stuff, and I just concentrate on the mahjong stuff.

### Scores stored as integers

In the Google scoresheet, scores are stored in their real form, as floats with one decimal place:
so +29.1 is stored as 29.1 And -5.0 is stored as -5.0.

On the server, in the cloud firestore, and in the app, scores are multiplied by 10 and stored as
 integers. That's to avoid any nonsense with inaccurate floating point arithmetic.
So a tournament score of +29.1 is stored as 291. A score of -5.0 is stored as -50.
Scores are expected to be received from the server in this form too.

The **only** place
where the conversion is done back to decimal, in the app, is at the final point of display. This
happens in [lib/score_cell.dart](lib/score_cell.dart#L12) and [server/run/run.py](server/run/run.py#L28)


### In the app, all state is in a single global variable

All of the state is stored in a single global state variable, of class AllState. I have no idea
as to whether that's a good way or a bad way to do it. [lib/store.dart](lib/store.dart#L53)

### There's no login for the app.

All info is public. This bypasses any issues around privacy policies, age requirements, etc.

There *are* logins for tournament admin and server admin on the web,
using Google oauth2 and Flask logins.

And the Google Sheet that is used for scoring for any given tournament,
has access permissions managed by Google.

That score sheet is not public: the only accounts that can see it,
will be the tournament scorers. We don't release the scores for a round, until
all games in that round have finished. This is important. It removes an incentive
to bad behaviour among players.

### App screenshots

<img src='https://github.com/applysci/aim/blob/main/pix/1p-seats.png?raw=true' width=200>
<img src='https://github.com/applysci/aim/blob/main/pix/all-seats.png?raw=true' width=200>
<img src='https://github.com/applysci/aim/blob/main/pix/scoresheet.png?raw=true' width=200>
