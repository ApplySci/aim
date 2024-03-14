// TODO this was all copied from previous app and needs checking

// TODO when a notif is received, download the latest tournament info

import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'store.dart';
import 'utils.dart';
/*

SharedPreference.reload(); when resuming

https://stackoverflow.com/questions/49869873/flutter-update-widgets-on-resume

Data only messages are considered low priority by devices when your application
is in the background or terminated, and will be ignored.
You can however explicitly increase the priority
by sending additional properties on the FCM payload:
On Android, set the priority field to high.

https://firebase.flutter.dev/docs/messaging/usage

handling notifs even when app not running:
Since the handler runs in its own isolate outside your applications context,
 it is not possible to update application state or execute any UI impacting logic.
 You can, however, perform logic such as HTTP requests, perform IO operations
 (e.g. updating local storage), communicate with other plugins etc.
 */

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  Log.debug("Handling a background message: ${message.messageId}");
  Log.debug("Message body: ${message.notification?.body}");
  _handleMessage(message);
}

FirebaseMessaging messaging = FirebaseMessaging.instance;

const AndroidNotificationChannel channel = AndroidNotificationChannel(
  'high_importance_channel', // id
  'High Importance Notifications', // title
  description: 'This channel is used for important notifications.',
  importance: Importance.high,
  playSound: true,
);

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

void subscribeUserToTopic() async {
  // subscribe to topic on each app start-up
  await messaging.subscribeToTopic('cork2024');
}

void unsubscribeUserToTopic() async {  // currently not called from anywhere
  await messaging.unsubscribeFromTopic('cork2024');
}

// iOS stuff:
void requestPermissionsOnMac() async {
  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false,
    provisional: false,
    sound: true,
  );

  Log.debug('User granted permission: ${settings.authorizationStatus}');
  // authorized, denied, notDetermined, provisional
}

Future<void> notifyWhenFocused(message) async {
  RemoteNotification? notification = message.notification;
  AndroidNotification? android = message.notification?.android;

  // If `onMessage` is triggered with a notification, construct our own
  // local notification to show to users using the created channel.
  if (notification != null && android != null) {
    AndroidNotificationDetails androidPlatformChannelSpecifics =
    AndroidNotificationDetails(
      channel.id,
      channel.name,
      channelDescription: channel.description,
      importance: channel.importance,
      priority: Priority.high,
      icon: 'aimbird',
      ticker: 'ticker',
    );

    NotificationDetails platformChannelSpecifics =
    NotificationDetails(android: androidPlatformChannelSpecifics);

    flutterLocalNotificationsPlugin.show(
      notification.hashCode,
      notification.title,
      notification.body,
      platformChannelSpecifics,
      payload: 'boom',
    );

    store.dispatch(STORE.setScores);
    store.dispatch(STORE.setPlayerList);
  }
}

buildAndNotify(String updateType) {
  // Future.delayed(const Duration(seconds: 1), () {
  //   print('One second has passed.'); // Prints after 1 second.
  // });
  // static List<String> messages;

  RemoteMessage message = RemoteMessage(
    notification: RemoteNotification(
      android: const AndroidNotification(),
      title: '$updateType has been updated',
    ),
    data: {'type': updateType,},
  );
  notifyWhenFocused(message);
}



void onIosSelectNotification(int num1, String? str1, String? str2, String? str3) async {
  Log.debug("Ios Notification received: $num1 $str1 $str2 $str3");
}

Future<void> setNotifierEvents() async {

  // app_icon @mipmap/ic_launcher
  const AndroidInitializationSettings initializationSettingsAndroid =  AndroidInitializationSettings('aimbird');

  const DarwinInitializationSettings initializationSettingsIOS =  DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
      onDidReceiveLocalNotification: onIosSelectNotification);

  const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
  );

  flutterLocalNotificationsPlugin.initialize(initializationSettings);

  await getFCMToken();
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  subscribeUserToTopic();

  await flutterLocalNotificationsPlugin
      .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin>()
      ?.createNotificationChannel(channel);

  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    // handle message received when app is in foreground
    notifyWhenFocused(message);
    _handleMessage(message);
  });
}

void notificationClickListener(
    BuildContext context, Map<String, dynamic> data) {
  // Extract notification message
  String message = data['message'] ?? 'Click listener pressed';

  // Display an alert with the "message" payload value
  showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
            title: const Text('Notification click'),
            content: Text(message),
            actions: [
              TextButton(
                  child: const Text('OK'),
                  onPressed: () {
                    Navigator.of(context, rootNavigator: true).pop('dialog');
                  })
            ]);
      });
}

Future<void> getFCMToken() async {
  final String fcmToken = await messaging.getToken() ?? '';

  Log.debug('FCM token: $fcmToken');

  messaging.onTokenRefresh.listen((fcmToken) {
    Log.debug('FCM token refreshed: $fcmToken');
    // Note: This callback is fired at each app startup and whenever a new
    // token is generated.
  }).onError((err) {
    // Error getting token.
  });
}

Future<void> setupInteractedMessage() async {
  // Get any messages which caused the application to open from
  // a terminated state.
  RemoteMessage? initialMessage =
      await messaging.getInitialMessage();

  if (initialMessage != null) {
    _handleMessage(initialMessage);
  }

  // Also handle any interaction when the app is in the background via a
  // Stream listener
  FirebaseMessaging.onMessageOpenedApp.listen(_handleMessage);
}

void _handleMessage(RemoteMessage message) {
  Log.debug('_handleMessage received a notification');
  Log.debug("Message body: ${message.notification?.body}");
  Log.debug("Message data: ${message.data}");
  // message.data['type'] message.data
}
