import 'package:firebase_messaging/firebase_messaging.dart';

import 'notifications.dart';
import 'utils.dart';

/// well, this seems to be working and captures cloud messages sent from
/// https://console.firebase.google.com/project/ie-mahjong-tournament/notification/compose
/// in foreground mode, background mode and when app is closed!
Future<void> setupFCM() async {

  await setNotifierEvents();
  // notifications work when app is closed, on Moto G54, Moto G 5G, and emulated
  await getFCMToken();
  setupInteractedMessage(); // Handle any incoming FCM notifications that caused the terminated app to re-open

  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  //subscribeUserToTopic(); // TODO get topic(s) from shared_preferences, probably

  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    // handle message received when app is in foreground
    // this works on Moto G 5G
    notifyWhenFocused(message);
    _handleMessage(message);
  });
}

// the following pragma prevents the function from being "optimised" out
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  /* TODO: Missing Default Notification Channel metadata in AndroidManifest.
           Default value will be used.

  "Since the handler runs in its own isolate outside your applications context,
  it is not possible to update application state or execute any UI impacting
  logic. You can, however, perform logic such as HTTP requests, perform IO
  operations (e.g. updating local storage), communicate with other plugins etc.

It is also recommended to complete your logic as soon as possible. Running long,
   intensive tasks impacts device performance and may cause the OS to terminate
   the process. If tasks run for longer than 30 seconds, the device may
   automatically kill the process."

   So maybe I should just leave a TODO in shared_preferences or something,
   to do the cloud store update when resume happens properly

   */
  Log.debug("Handling a background message: ${message.messageId}");
  Log.debug("Message body: ${message.notification?.body}");
  _handleMessage(message);
}

void subscribeUserToTopic(String tournament) async {
  // TODO not yet called from anywhere
  // subscribe to topic on each app start-up
  await messaging.subscribeToTopic(tournament);
}

void unsubscribeUserToTopic(String tournament) async {
  // TODO not yet called from anywhere
  await messaging.unsubscribeFromTopic(tournament);
}

Future<void> getFCMToken() async {
  final String fcmToken = await messaging.getToken() ?? '';

  Log.debug('FCM token: $fcmToken');
  // TODO send it to our server

  messaging.onTokenRefresh.listen((fcmToken) {
    Log.debug('FCM token refreshed: $fcmToken');
    // TODO send it to our server
    // Note: This callback is fired at each app startup and whenever a new
    // token is generated.
  }).onError((err) {
    Log.error('Failed to set listener for fcmToken in onTokenRefresh: ${err.message}');
    // Error getting token.
  });
}

Future<void> setupInteractedMessage() async {
  // Get any messages which caused the application to open from
  // a terminated state.
  RemoteMessage? initialMessage = await messaging.getInitialMessage();

  if (initialMessage != null) {
    _handleMessage(initialMessage);
  }

  // Also handle any interaction when the app is in the background via a
  // Stream listener
  FirebaseMessaging.onMessageOpenedApp.listen(_handleMessage);
}

void _handleMessage(RemoteMessage message) {
  Log.debug('_handleMessage received a notification');
  Log.debug("Title: ${message.notification?.title}");
  Log.debug("body: ${message.notification?.body}");
  Log.debug("data: ${message.data}");
  // contentAvailable collapseKey category senderId
  // message.data['type'] message.data
}
