# World Riichi App for Tournaments

This is the [World Riichi](https://worldriichi.org/) mobile app.
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

A tournament admin is able to do everything through a web interface.
It's designed in a way that a browser with 3 tabs can do everything:

- the admin web interface
- the google scoring sheet; and
- the live web page;

## Programming platforms, frameworks & languages used

The client-side written in Dart with the **Flutter** framework. It's developed and
tested for **android**, in Android Studio, and for iPhone & iPad(Mini) on xCode.

The server-side is written in **Python (3.10+)**, with the **Flask** framework. See [server/README.md](server/README.md) for details.
I'm running it
on the server with **gunicorn**. Note that the oauth2 authentication won't work on localhost: you need
a google project that knows about the domain that the app is being served from, and must be given
the post-authentication URL to redirect back to.  **GSPRead** is used to read the
scoresheet, to create the live score web page, and to put the data into the
cloud, for onward transmission to the app

App notifications are by **Firebase Cloud Messaging**.
And via **APN**, for IOS.
Live tournament data is stored in **Google Cloud Firestore**.

When the app has a connection, and is in foreground or background, any update to
the firebase cloud data gets noticed by the listener.
If the app is closed, then it won't know anything about it, so the server sends FCM notifications
to all subscribed devices.

The live scoring of a tournament is done in a **Google spreadsheet**,
based on the one developed by David Bresnick for the World Riichi Championship.

### In the app, all state is managed by Riverpod

Thanks to fantastic work by [@North101](https://github.com/North101),
all of the state is now managed by [Riverpod](https://riverpod.dev/) providers & listeners


## Coding decisions that might be unexpected (and might be unsound):

### Going via firebase cloud store for the data, rather than server -> app directly

I've had a few trial run-ups at it, and after a few false starts, have settled on
google firebase & cloud messaging because it will be free for the level of use I'm anticipating,
and because it takes care of loads of messy stuff such as background syncing of
data between mobiles and server, and caching stuff on mobile so that everything
behaves just perfectly even when the mobile has patchy signal. I did try crafting my own
local caching thing for android, and it was super messy, so it just made sense to let google
do all the clever io stuff, and I just concentrate on the mahjong stuff. Past tournaments *are*
stored on server, rather than in-cloud, as their number will just grow and grow.

### Scores stored as integers

In the Google scoresheet, scores are stored in their real form, as floats with one decimal place:
so +29.1 is stored as 29.1 And -5.0 is stored as -5.0.

**On the server, in the cloud firestore, and in the app, scores are multiplied by 10 and stored as
 integers.** That's to avoid any nonsense with inaccurate floating point arithmetic.
So a tournament score of +29.1 is stored as 291. A score of -5.0 is stored as -50.
Scores are expected to be received from the server in this form too.

The **only** place
where the conversion is done back to decimal, in the app, is at the final point of display. This
happens in [lib/score_cell.dart](lib/score_cell.dart#L12) and [server/run/run.py](server/run/run.py#L28)

### There's no login for the app.

All info is public. This bypasses any issues around privacy policies, age requirements, etc.

There *are* logins for tournament admin and server admin on the web,
using Google oauth2, so everyone who's going to run or score a tournament needs a google account.

And the Google Sheet that is used for scoring for any given tournament,
has access permissions managed by Google.

That score sheet is not public: the only accounts that can see it,
will be the tournament scorers. We don't release the scores for a round, until
all games in that round have finished. This is important. It removes an incentive
to bad behaviour among players.


### App screenshots (TODO - UPDATE)

<img src='https://github.com/applysci/aim/blob/main/pix/1p-seats.png?raw=true' width=200>
<img src='https://github.com/applysci/aim/blob/main/pix/all-seats.png?raw=true' width=200>
<img src='https://github.com/applysci/aim/blob/main/pix/scoresheet.png?raw=true' width=200>


# If you're creating your own version of this app

If you're creating your own version of this app, rather than running off my instance,
you'll need to set up the cloud stuff. I've tried to remember all the steps, but there are probably some missing.
- First you'll need a google cloud project.
- Create a `(default)` firestore database, and give it a `tournaments` collection,
and a `metadata` collection containing a past_tournaments document with a field `api_base_url` with
the base URL of your server.
- In the google console:
  - Give third-party read-only permissions to the database.
  - Enable the google drive API, and the Sheets API.
  - Then you'll need a google-services.json and GoogleServices.plist file from it
  - Configure the Google Auth Platform
  - Create a Google OAuth Client - you'll need the client ID and client secret for the `server/config.py` file
  - and generate a new private key to access the database - save this as `fcm-admin.json`
-   There will be a google service account with an email of the form: `firebase-adminsdk-{something}@domain-name-backwards-with-dashes.iam.gserviceaccount.com`. Make sure this email address has editor permissions for the google sheet score template.
- You'll need an account on the play store to distribute the app.

## APN - Apple Push Notifications
Once you've got the google firebase cloud messaging working, you'll need to set up the APN to reach Apple devices.

First, an APN authentication key is needed:

- Go to the Apple Developer website (https://developer.apple.com/) and sign in.
- Navigate to "Certificates, Identifiers & Profiles".
- In the left sidebar, under "Keys", click on "All".
- Click the "+" button to create a new key.
- Give your key a name (e.g., "Firebase APNs Key").
- Check the box for "Apple Push Notifications service (APNs)".
- Click "Continue" and then "Register".
- Download the key file (.p8). You'll only be able to download it once, so keep it safe.
- Note the Key ID and the Team ID (visible in the top right of the page).

The p8 key file, Key ID and Team ID then go into the firebase console.

Check your App ID:
- In the left sidebar, click on "Certificates, Identifiers & Profiles".
- Under "Identifiers", click on "App IDs".
- Find your app's identifier (it should match your bundle ID - ie.mahjong.tournament).
- Click on it and ensure that "Push Notifications" is enabled in the capabilities list.

Check your Certificates:
- In the left sidebar, under "Certificates, Identifiers & Profiles", click on "Certificates".
- You should see an Apple Push Notification service SSL (Sandbox & Production) certificate for the app. You'll need this on the device where you compile the Apple version of the app.
- If it's expired, you'll need to create a new one.

Create a new Push Notification Certificate if needed:
- Click the "+" button to add a new certificate.
- Select "Apple Push Notification service SSL (Sandbox & Production)".
- Choose the App ID for your application.
- Follow the instructions to create a Certificate Signing Request (CSR) using Keychain Access on your Mac.
- Upload the CSR and download the resulting certificate.

Install the certificate on the device where you compile the Apple version of the app:
- Double-click the downloaded certificate to install it in your Keychain

Regenerate Provisioning Profile:
- Back in the Apple Developer portal, go to "Profiles".
- Find your app's provisioning profile.
- Click on it and then click "Edit".
- No changes are necessary, just proceed through the steps and regenerate the profile.
- Download the new profile.

Update Xcode:
- In Xcode, go to Xcode > Preferences > Accounts.
- Select your Apple ID and click "Download Manual Profiles" or "Refresh".
- Close Preferences and select your project in the Project Navigator.
- In the "Signing & Capabilities" tab, ensure that the newly downloaded provisioning profile is selected.

After completing these steps, clean and rebuild your project in Xcode. This should ensure that your app is using the correct certificates and provisioning profile for push notifications.

You'll need an account on the Apple store. It can take several days to get approved,
and several more to get your app approved.
