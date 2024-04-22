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
  Log.debug("Handling a background message: ${message.messageId}");
  Log.debug("Message body: ${message.notification?.body}");
  _handleMessage(message);
}

// TODO offer the user a notification-reset option, by forcing fcm token refresh

Future<void> subscribeUserToTopic(String topic, String? previous) async {
  // this subscription persists through app restarts and changes of token
  if (previous != null) {
    // we await the unsubscribe, to avoid a race between subscribe & unsubscribe
    //   if the user re-selects the same thing
    Log.debug("FCM unsubscribing from $topic");
    await messaging.unsubscribeFromTopic(previous);
  }
  Log.debug("FCM subscribing to $topic");
  messaging.subscribeToTopic(topic);
}


Future<void> getFCMToken() async {
  final String fcmToken = await messaging.getToken() ?? '';

  messaging.onTokenRefresh.listen((fcmToken) {
    Log.debug('FCM token refreshed: $fcmToken');
    // TODO may need to re-do all the subscriptions
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
