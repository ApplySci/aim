// TODO this was all copied from previous app and needs checking

// TODO when a notif is received, download the latest tournament info

import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'client.dart';
import 'firebase_options.dart';
import 'store.dart';
import 'utils.dart';
/*

Updating widgets when app is resumed:
https://stackoverflow.com/questions/49869873/flutter-update-widgets-on-resume


SharedPreference.reload(); when resuming

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


const AndroidNotificationChannel channel = AndroidNotificationChannel(
// TODO doesn't seem to do anything yet, even when a message is sent in the aim112 channel
  'aim112', // id
  'High Importance Notifications', // title
  description: 'This channel is used for important notifications.',
  importance: Importance.high,
  playSound: true,
);

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

Future<void> requestPermissions() async { // tested, works
  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false, // this is for emergency services and the like. Not us
    provisional: false,
    sound: true,
  );

  Log.debug('User response to request for messaging permission: '
      '${settings.authorizationStatus}');
  // authorized, denied, notDetermined, provisional

  bool? alarms = await flutterLocalNotificationsPlugin
      .resolvePlatformSpecificImplementation<
      AndroidFlutterLocalNotificationsPlugin>()
      ?.requestExactAlarmsPermission();

  Log.debug('User response to request for alarms permission: $alarms');

}


Future<void> _showNotification() async {
  // TODO schedule a notification for just before a hanchan starts
  //      add the following to the zonedSchedule notifications:
  //      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
  // or androidScheduleMode: AndroidScheduleMode.alarmClock
  // see https://developer.android.com/develop/background-work/services/alarms/schedule#set-exact-alarm
  var androidPlatformChannelSpecifics = const AndroidNotificationDetails(
    'channel_ID',
    'channel_name',
    channelDescription: 'channel_description',
    importance: Importance.max,
    priority: Priority.high,
  );
  var iOSPlatformChannelSpecifics = const DarwinNotificationDetails();
  var platformChannelSpecifics = NotificationDetails(
    android: androidPlatformChannelSpecifics,
    iOS: iOSPlatformChannelSpecifics,
  );
  await flutterLocalNotificationsPlugin.show(
    0,
    'Test Title',
    'Test Body',
    platformChannelSpecifics,
    payload: 'Test Payload',
  );
}

Future<void> notifyWhenFocused(message) async { // called from fcm_client
  // worked on Moto G 5G
  // But it's not at all clear that it's useful
  // TODO just do a snackbar instead
  RemoteNotification? notification = message.notification;
  AndroidNotification? android = message.notification?.android;

  Log.debug('in notifyWhenFocused');
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
      actions: [
        AndroidNotificationAction('action_1', 'Action 1', showsUserInterface: true),
        AndroidNotificationAction('action_2', 'Action 2', showsUserInterface: true),
      ],
      styleInformation: BigTextStyleInformation(
        'styleInformation text',
        contentTitle: 'styleInformation contentTitle',
      ),
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


  }
}

buildAndNotify(String updateType) {

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
  Log.debug("IOS Notification received: $num1 $str1 $str2 $str3");
}


// https://stackoverflow.com/questions/76561585/flutter-local-notification-action-button-click-not-working
Future<void> setNotifierEvents() async {
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  const AndroidInitializationSettings initAndroid =
  AndroidInitializationSettings('aimbird');

  const DarwinInitializationSettings initIOS =
  DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
      onDidReceiveLocalNotification: onIosSelectNotification);

  const InitializationSettings initializationSettings = InitializationSettings(
    android: initAndroid,
    iOS: initIOS,
  );

  var notifPlatform = await flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
  );

  await requestPermissions();

  await flutterLocalNotificationsPlugin
      .resolvePlatformSpecificImplementation<
      AndroidFlutterLocalNotificationsPlugin>()
      ?.createNotificationChannel(channel);
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


Future<void> _startForegroundServiceWithBlueBackgroundNotification() async {
  const AndroidNotificationDetails androidPlatformChannelSpecifics =
  AndroidNotificationDetails(
    'your channel id',
    'your channel name',
    channelDescription: 'color background channel description',
    importance: Importance.max,
    priority: Priority.high,
    ticker: 'ticker',
    color: Colors.blue,
    colorized: true,
  );

  /// only using foreground service can color the background
  await flutterLocalNotificationsPlugin
      .resolvePlatformSpecificImplementation<
      AndroidFlutterLocalNotificationsPlugin>()
      ?.startForegroundService(
      1, 'colored background text title', 'colored background text body',
      notificationDetails: androidPlatformChannelSpecifics,
      payload: 'item x');
}
