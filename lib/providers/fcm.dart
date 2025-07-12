import 'dart:async';
import 'dart:io' show Platform;

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest_10y.dart';

import '/firebase_options.dart';
import '/services/alarm_service.dart';
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
    Log.debug('=== handleMessage START ===');
    Log.debug('Firebase apps available: ${Firebase.apps.length}');
    
    if (!Firebase.apps.isNotEmpty) {
      Log.debug('Firebase not initialized, skipping message handling');
      return;
    }

    final data = message.data;
    Log.debug('Full message data: $data');
    
    final tournamentId = data['tournament_id'];
    final notificationType = data['notification_type'];

    Log.debug('Extracted - tournamentId: $tournamentId, notificationType: $notificationType');

    if (tournamentId == null || notificationType == null) {
      Log.debug('Missing required notification data - skipping');
      return;
    }

    // Only store notification data in preferences
    SharedPreferences.getInstance().then((prefs) {
      Log.debug('Storing notification data in preferences');
      prefs.setString(notificationTournamentKey, tournamentId);
      prefs.setString(notificationTabKey, notificationType);
      Log.debug('Successfully stored notification data');
    }).catchError((e) {
      Log.error('Error storing notification data: $e');
    });

    Log.debug('=== handleMessage END ===');
  } catch (e, stack) {
    Log.error('Error in handleMessage: $e');
    Log.debug('Stack trace: $stack');
  }
}

void handleNotificationOpen(RemoteMessage message) {
  try {
    Log.debug('=== handleNotificationOpen START ===');
    final data = message.data;
    final tournamentId = data['tournament_id'];
    final notificationType = data['notification_type'];

    Log.debug('Navigation - tournamentId: $tournamentId, notificationType: $notificationType');

    if (tournamentId == null) {
      Log.debug('Missing tournament_id in notification');
      return;
    }

    final navigator = globalNavigatorKey.currentState;
    Log.debug('Navigator available: ${navigator != null}');

    if (navigator != null) {
      navigator.popAndPushNamed(
        ROUTES.tournament,
        arguments: {
          'tournament_id': tournamentId,
          'initial_tab': notificationType,
        },
      );
      Log.debug('Navigation completed successfully');
    } else {
      Log.debug('No navigator available for navigation');
    }

    Log.debug('=== handleNotificationOpen END ===');
  } catch (e, stack) {
    Log.error('Error in handleNotificationOpen: $e');
    Log.debug('Stack trace: $stack');
  }
}

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  try {
    Log.debug('🔥🔥🔥 BACKGROUND HANDLER TRIGGERED 🔥🔥🔥');
    Log.debug('Message received at: ${DateTime.now().toIso8601String()}');
    Log.debug('Message from: ${message.from}');
    Log.debug('Message messageId: ${message.messageId}');
    Log.debug('Message notification title: ${message.notification?.title}');
    Log.debug('Message notification body: ${message.notification?.body}');
    Log.debug('Message data: ${message.data}');
    
    // Initialize Firebase first
    Log.debug('Initializing Firebase...');
    await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
    Log.debug('Firebase initialized successfully');
    
    // Initialize timezone database for background processing
    Log.debug('Initializing timezone database...');
    try {
      initializeTimeZones();
      Log.debug('Timezone database initialized successfully');
    } catch (e) {
      Log.error('Error initializing timezone database: $e');
      // Continue anyway, the AlarmService will handle timezone issues gracefully
    }
    
    // Parse message data
    final data = message.data;
    final tournamentId = data['tournament_id'];
    final notificationType = data['notification_type'];
    
    Log.debug('Parsed data - tournamentId: $tournamentId, notificationType: $notificationType');
    
    // Check if this is a schedule update (either 'schedule' or 'seating' can affect alarms)
    if (notificationType == 'schedule' || notificationType == 'seating') {
      Log.debug('🔔 SCHEDULE/SEATING UPDATE DETECTED - Processing alarm update');
      
      // Get current alarm preferences
      final prefs = await SharedPreferences.getInstance();
      final alarmsEnabled = prefs.getBool('alarm') ?? true;
      final currentTournamentId = prefs.getString('tournamentId');
      
      Log.debug('Current app state:');
      Log.debug('  - Alarms enabled: $alarmsEnabled');
      Log.debug('  - Current tournament ID: $currentTournamentId');
      Log.debug('  - Message tournament ID: $tournamentId');
      
      if (!alarmsEnabled) {
        Log.debug('❌ Alarms disabled - skipping alarm update');
      } else if (currentTournamentId != tournamentId) {
        Log.debug('❌ Tournament mismatch - skipping alarm update');
        Log.debug('    Current: "$currentTournamentId" vs Message: "$tournamentId"');
      } else {
        Log.debug('✅ Processing alarm update for tournament: $tournamentId');
        
        try {
          await AlarmService.handleScheduleUpdateMessage(message);
          Log.debug('✅ Alarm service completed successfully');
        } catch (e, stack) {
          Log.error('❌ Error in AlarmService.handleScheduleUpdateMessage: $e');
          Log.debug('Stack trace: $stack');
        }
      }
    } else {
      Log.debug('📋 Not a schedule/seating update (type: $notificationType) - skipping alarm update');
    }
    
    // Continue with existing message handling
    Log.debug('Processing standard message handling...');
    handleMessage(message);
    
    Log.debug('🟢 BACKGROUND HANDLER COMPLETED SUCCESSFULLY 🟢');
  } catch (e, stack) {
    Log.error('💥 CRITICAL ERROR IN BACKGROUND HANDLER: $e');
    Log.debug('Stack trace: $stack');
  }
}

Future<void> initFirebaseMessaging() async {
  try {
    Log.debug('initializing firebase');
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );

    final prefs = await SharedPreferences.getInstance();
    final topics = prefs.getString('fcm_topics');

    // If no topics record exists (not even empty list), we'll need to handle this in migration
    // but we'll continue with FCM initialization regardless
    if (topics == null) {
      Log.debug('No FCM topics record found, will handle this in migration, but continuing with FCM initialization');
      // Save an empty topics list to prevent future migrations from running unnecessarily
      await prefs.setString('fcm_topics', '[]');
    }

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

    // Get token directly instead of using a callback to ensure proper async flow
    Log.debug('Getting FCM token directly');
    final token = await FirebaseMessaging.instance.getToken();
    if (token == null) {
      Log.debug('Failed to get FCM token');
      return;
    }
    Log.debug('FCM Token obtained: ${token.substring(0, 10)}...');

    // Register background handler
    Log.debug('Register background handler');
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

    // Configure how to handle notifications when app is in foreground
    Log.debug('Handle foreground notifications');
    await FirebaseMessaging.instance.setForegroundNotificationPresentationOptions(
      alert: true,
      badge: true,
      sound: true,
    );

    // user has tapped on notification to open killed app
    final initialMessage = await FirebaseMessaging.instance.getInitialMessage();
    if (initialMessage != null) {
      Log.debug('in initFirebaseMessaging with initialMessage');
      handleNotificationOpen(initialMessage);
    }

    // user has tapped on notification to bring backgrounded app to the foreground
    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      Log.debug(
          'in initFirebaseMessaging/onMessageOpenedApp - ${message.data}');
      handleNotificationOpen(message);
    });

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((message) {
      Log.debug('🔔 FOREGROUND MESSAGE RECEIVED');
      Log.debug('Message data: ${message.data}');
      Log.debug('Message notification: ${message.notification?.title}');

      // Handle schedule updates in foreground too
      final data = message.data;
      final notificationType = data['notification_type'];
      
      if (notificationType == 'schedule' || notificationType == 'seating') {
        Log.debug('🔔 Processing schedule/seating update in FOREGROUND');
        Future(() async {
          try {
            await AlarmService.handleScheduleUpdateMessage(message);
            Log.debug('✅ Foreground alarm update completed');
          } catch (e, stack) {
            Log.error('❌ Error in foreground alarm update: $e');
            Log.debug('Stack trace: $stack');
          }
        });
      }

      final notification = message.notification;
      if (notification != null) {
        final context = globalNavigatorKey.currentState?.overlay?.context;
        if (context == null || !context.mounted) {
          Log.debug('No context available for snackbar');
          return;
        }
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
        Log.debug('Displayed notification snackbar');
      }
    });
    
    // For diagnostic purposes - log subscribed topics
    try {
      final topicsString = prefs.getString('fcm_topics');
      if (topicsString != null) {
        Log.debug('Currently subscribed FCM topics: $topicsString');
      } else {
        Log.debug('No FCM topics found in preferences');
      }
    } catch (e) {
      Log.debug('Error checking FCM topics: $e');
    }
  } catch (e, stack) {
    Log.debug('Firebase Messaging initialization failed: $e');
    Log.debug('Stack trace: $stack');
    // Continue app initialization even if FCM fails
  }
  Log.debug('finished initializing firebase');
}
