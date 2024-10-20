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
  await FirebaseMessaging.instance.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false, // this is for emergency services and the like. Not us
    provisional: false,
    sound: true,
  );
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
}

// the following pragma prevents the function from being "optimised" out
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  Log.debug('Handling a background message: ${message.messageId}');
  Log.debug('Message body: ${message.notification?.body}');
  // TODO may need to update values if app is in background - particularly if schedule is updated - we must update alarms
}

Future<void> initPermissions() async {
  final status = await Permission.scheduleExactAlarm.status;
  if (status.isDenied) {
    await Permission.scheduleExactAlarm.request();
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized(); // do this before everything

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.black, //top bar color
    statusBarIconBrightness: Brightness.light, //top bar icons
    systemNavigationBarColor: Colors.black, //bottom bar color
    systemNavigationBarIconBrightness: Brightness.light, //bottom bar icons
  ));

  initializeTimeZones();

  // Separate Firebase initialization
  try {
    await initFirebase();
    await initFirebaseMessaging();
  } catch (e) {
    Log.error('Failed to initialize Firebase: $e');
    // Continue with the app even if Firebase fails
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
