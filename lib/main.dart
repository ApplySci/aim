import 'dart:async';
import 'dart:io' show Platform;

import 'package:alarm/alarm.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest_10y.dart';

import 'firebase_options.dart';
import 'models.dart';
import 'providers.dart';
import 'utils.dart';
import 'views/alarm_page.dart';
import 'views/player_page/player_page.dart';
import 'views/round_page/round_page.dart';
import 'views/settings_page.dart';
import 'views/tournament_list_page.dart';
import 'views/tournament_page/page.dart';

Future<void> initFirebase() => Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );

Future<void> initFirebaseMessaging() async {
  final settings = await FirebaseMessaging.instance.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false,
    provisional: false,
    sound: true,
  );

  Log.debug('FCM Authorization status: ${settings.authorizationStatus}');
  Log.debug('Alert setting: ${settings.alert}');
  Log.debug('Sound setting: ${settings.sound}');

  // Get FCM token and log it
  final token = await FirebaseMessaging.instance.getToken();
  Log.debug('FCM Token: $token');

  // Configure how to handle notifications when app is in foreground
  await FirebaseMessaging.instance.setForegroundNotificationPresentationOptions(
    alert: true,
    badge: true,
    sound: true,
  );

  // Handle notification open when app is terminated
  final initialMessage = await FirebaseMessaging.instance.getInitialMessage();
  if (initialMessage != null) {
    _handleMessage(initialMessage);
  }

  // Handle notification open when app is in background
  FirebaseMessaging.onMessageOpenedApp.listen(_handleMessage);

  // Handle foreground messages
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    Log.debug('Got a message whilst in the foreground!');
    Log.debug('Message data: ${message.data}');
    if (message.notification != null) {
      Log.debug('Message also contained notification: ${message.notification}');
    }
  });
}

void _handleMessage(RemoteMessage message) {
  Log.debug('Handling message: ${message.messageId}');
  // Add any navigation or state handling logic here
  // For now, just log the message
  Log.debug('Message data: ${message.data}');
  Log.debug('Message notification: ${message.notification}');
}

// the following pragma prevents the function from being "optimised" out
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  Log.debug('Handling a background message ${message.messageId}');
  Log.debug('Notification: ${message.notification?.title}');
  Log.debug('Data: ${message.data}');
}

Future<void> initPermissions() async {
  final status = await Permission.scheduleExactAlarm.status;
  if (status.isDenied) {
    await Permission.scheduleExactAlarm.request();
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Register background handler BEFORE Firebase init
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.black,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: Colors.black,
    systemNavigationBarIconBrightness: Brightness.light,
  ));

  initializeTimeZones();

  try {
    await initFirebase();
    await initFirebaseMessaging();
  } catch (e) {
    Log.error('Failed to initialize Firebase: $e');
  }

  // Always initialize permissions and alarms
  await initPermissions();
  try {
    await Alarm.init();
  } catch (e) {
    Log.error('Failed to initialize Alarm: $e');
    // Handle alarm initialization failure
  }

  runApp(ProviderScope(
    overrides: [
      sharedPreferencesProvider.overrideWithValue(
        await SharedPreferences.getInstance(),
      ),
    ],
    child: _MyApp(),
  ));
}

class _MyApp extends ConsumerWidget {
  // Unhandled Exception: Looking up a deactivated widget's ancestor is unsafe.
  // E/flutter ( 5008): At this point the state of the widget's element tree is no longer stable.
  openAlarmPage(BuildContext context, AlarmSettings settings) {
    if (settings.dateTime
        .isAfter(DateTime.now().subtract(const Duration(minutes: 30)))) {
      globalNavigatorKey.currentState?.push(
        MaterialPageRoute<void>(
          builder: (context) => AlarmPage(settings: settings),
        ),
      );
    }
  }

  @override
  Widget build(context, ref) {
    final fcm = ref.watch(fcmProvider);

    // Open alarm screen when alarm rings
    ref.listenAsyncData(
      alarmRingProvider,
      (prev, next) => openAlarmPage(context, next),
    );

    // Set alarms when alarm schedule updates
    ref.listenAsyncData(
      alarmScheduleProvider,
      (prev, next) => alarmRunner(() async {
        final now = DateTime.now().toUtc();
        await Alarm.stopAll();

        final vibratePref = ref.read(vibratePrefProvider);

        // set one alarm for each round
        for (final (index, (id: _, :name, :alarm, :player)) in next.indexed) {
          if (now.isBefore(alarm)) {
            final title = '$name starts in 5 minutes';
            final body = player != null
                ? '${player.name} is at table ${player.table}'
                : '';
            await setAlarm(alarm, title, body, index + 1, vibratePref);
          }
        }
      }),
    );

    // Update firebase subscription when tournamentId changes
    ref.listen(
      tournamentIdProvider,
      (prev, next) {
        if (prev case TournamentId tournamentId) {
          fcm.unsubscribeFromTopic(tournamentId);
        }
        if (next case TournamentId tournamentId) {
          fcm.subscribeToTopic(tournamentId);
        }
      },
    );

    // Update firebase subscription when tournamentId or playerId changes
    ref.listen(
      tournamentPlayerIdProvider,
      (prev, next) {
        if (prev case (:TournamentId tournamentId, :PlayerId playerId)) {
          fcm.unsubscribeFromTopic('$tournamentId-$playerId');
        }
        if (next case (:TournamentId tournamentId, :PlayerId playerId)) {
          fcm.subscribeToTopic('$tournamentId-$playerId');
        }
      },
    );

    // Handle fcm tokens
    ref.listenAsyncData(
      fcmTokenProvider,
      (prev, next) {
        Log.debug('FCM token refreshed: $next');
      },
    );

    if (Platform.isIOS) {
      // apple notifications
      ref.listenAsyncData(
        apnsTokenProvider,
        (prev, next) {
          Log.debug('APNS token refreshed: $next');
        },
      );
    }
    // Handle fcm messages
    ref.listenAsyncData(
      fcmMessagesProvider,
      (prev, next) {
        Log.debug('fcmMessagesProvider received a notification');
        Log.debug('Title: ${next.notification?.title}');
        Log.debug('body: ${next.notification?.body}');
        Log.debug('data: ${next.data}');
      },
    );

    final lightTheme = ThemeData.light(useMaterial3: true);
    final darkTheme = ThemeData.dark(useMaterial3: true);
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: ROUTES.home,
      navigatorKey: globalNavigatorKey,
      title: 'All-Ireland Mahjong Tournaments',
      theme: lightTheme.copyWith(
        appBarTheme: AppBarTheme(
          backgroundColor: lightTheme.colorScheme.inversePrimary,
        ),
      ),
      darkTheme: darkTheme.copyWith(
        appBarTheme: AppBarTheme(
          backgroundColor: darkTheme.colorScheme.inversePrimary,
        ),
      ),
      themeMode: ThemeMode.system,
      routes: {
        ROUTES.home: (context) => const TournamentListPage(),
        ROUTES.settings: (context) => const SettingsPage(),
        ROUTES.tournaments: (context) => const TournamentListPage(),
        ROUTES.tournament: (context) => const TournamentPage(),
        ROUTES.player: (context) => const PlayerPage(),
        ROUTES.round: (context) => const RoundPage(),
      },
    );
  }
}
