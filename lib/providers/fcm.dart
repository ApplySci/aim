import 'dart:async';
import 'dart:io' show Platform;

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '/firebase_options.dart';
import '/utils.dart';

final fcmProvider = Provider((ref) => FirebaseMessaging.instance);

final fcmTokenProvider = StreamProvider((ref) async* {
  final fcm = ref.watch(fcmProvider);
  yield await fcm.getToken() ?? '';
  yield* FirebaseMessaging.instance.onTokenRefresh;
});

final apnsTokenProvider = StreamProvider((ref) async* {
  if (!const bool.fromEnvironment('dart.vm.product')) {
    yield '';
    return;
  }

  final fcm = ref.watch(fcmProvider);
  yield await fcm.getAPNSToken() ?? '';
  yield* FirebaseMessaging.instance.onTokenRefresh;
});

final fcmMessagesProvider = StreamProvider((ref) async* {
  final fcm = ref.watch(fcmProvider);
  final initialMessage = await fcm.getInitialMessage();
  if (initialMessage != null) yield initialMessage;

  final controller = StreamController<RemoteMessage>();
  ref.onDispose(() => controller.close());

  FirebaseMessaging.onMessage.pipe(controller);
  FirebaseMessaging.onMessageOpenedApp.pipe(controller);

  yield* controller.stream;
});

void handleMessage(RemoteMessage message) {
  try {
    if (!Firebase.apps.isNotEmpty) {
      Log.debug('Firebase not initialized, skipping message handling');
      return;
    }

    final data = message.data;
    final tournamentId = data['tournament_id'];
    final notificationType = data['notification_type'];

    Log.debug('Handling message with type: $notificationType');

    if (tournamentId == null || notificationType == null) {
      Log.debug('Missing required notification data');
      return;
    }

    // Only store notification data in preferences
    SharedPreferences.getInstance().then((prefs) {
      prefs.setString(notificationTournamentKey, tournamentId);
      prefs.setString(notificationTabKey, notificationType);
      Log.debug('Stored notification data in preferences');
    });

  } catch (e, stack) {
    Log.debug('Error handling message: $e');
    Log.debug('Stack trace: $stack');
  }
}

void handleNotificationOpen(RemoteMessage message) {
  try {
    final data = message.data;
    final tournamentId = data['tournament_id'];
    final notificationType = data['notification_type'];

    if (tournamentId == null) {
      Log.debug('Missing tournament_id in notification');
      return;
    }

    globalNavigatorKey.currentState?.popAndPushNamed(
      ROUTES.tournament,
      arguments: {
        'tournament_id': tournamentId,
        'initial_tab': notificationType,
      },
    );

  } catch (e, stack) {
    Log.debug('Error handling notification open: $e');
    Log.debug('Stack trace: $stack');
  }
}

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  try {
    await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
    Log.debug('in firebaseMessagingBackgroundHandler:');
  } catch (e) {
    Log.warn('Error in background handler: $e');
  }
}


Future<void> initFirebaseMessaging() async {
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    await FirebaseMessaging.instance.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );
    // Skip FCM initialization in debug mode in ios
    if (Platform.isIOS && !const bool.fromEnvironment('dart.vm.product')) {
      Log.debug('Skipping FCM initialization in iOS simulator');
      return;
    }

    FirebaseMessaging.instance.getToken().then((String? token) {
      if (token == null) {
        Log.debug('Failed to get FCM token');
        return;
      }
      Log.debug('FCM Token: $token');

      // Register background handler
      FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);


      // Configure how to handle notifications when app is in foreground
      FirebaseMessaging.instance.setForegroundNotificationPresentationOptions(
        alert: true,
        badge: true,
        sound: true,
      );

      // user has tapped on notification to open killed app
      FirebaseMessaging.instance.getInitialMessage().then((message) {
        if (message != null) {
          Log.debug('in initFirebaseMessaging with initialMessage');
          handleNotificationOpen(message);
        }
      });

      // user has tapped on notification to bring backgrounded app to the foreground
      FirebaseMessaging.onMessageOpenedApp.listen((message) {
        Log.debug(
            'in initFirebaseMessaging/onMessageOpenedApp - ${message.data}');
        handleNotificationOpen(message);
      });

      // Handle foreground messages
      FirebaseMessaging.onMessage.listen((message) {
        Log.debug('In initFirebaseMessaging/onMessage');

        final notification = message.notification;
        if (notification != null) {
          final context = globalNavigatorKey.currentState?.overlay?.context;
          if (context == null || !context.mounted) return;
          final scaffoldMessenger = ScaffoldMessenger.of(context);

          scaffoldMessenger.showSnackBar(
            SnackBar(
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(notification.title ?? ''),
                  if (notification.body != null)
                    Text(
                      notification.body!,
                      style: const TextStyle(fontSize: 12),
                    ),
                ],
              ),
            ),
          );
        }
      });
    });
  } catch (e) {
    Log.debug('Firebase Messaging initialization failed: $e');
    // Continue app initialization even if FCM fails
  }
}
