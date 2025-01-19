# Notes for forkers

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

From the command-line, install the Firebase CLI and generate your firebase_options.dart file:
```
npm install -g firebase-tools
dart pub global activate flutterfire_cli
firebase login
flutterfire configure
```

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
- Find your app's identifier (it should match your bundle ID, eg `ie.mahjong.tournament`).
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
