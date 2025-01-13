import 'dart:async';
import 'dart:io' show Platform;
import 'dart:collection';

import 'package:alarm/alarm.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_fgbg/flutter_fgbg.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest_10y.dart';

import 'models.dart';
import 'providers.dart';
import 'utils.dart';
import 'views/alarm_page.dart';
import 'views/player/player_page.dart';
import 'views/round/round_page.dart';
import 'views/settings_page.dart';
import 'views/tournament_list_page.dart';
import 'views/tournament/tournament_page.dart';

StreamSubscription<AlarmSettings>? ringSubscription;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase core before anything else
  try {
    // and initialize messaging
    await initFirebaseMessaging();

  } catch (e, stack) {
    Log.debug('Firebase initialization error: $e');
    Log.debug('Stack trace: $stack');
  }

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.black,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: Colors.black,
    systemNavigationBarIconBrightness: Brightness.light,
  ));

  initializeTimeZones();

  // Always initialize permissions and alarms
  await initPermissions();
  try {
    await Alarm.init();
    ringSubscription = Alarm.ringStream.stream.listen(openAlarmPage);
    checkAlarms();
  } catch (e) {
    Log.error('Failed to initialize Alarm: $e');
    // TODO Handle alarm initialization failure
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

  @override
  Widget build(context, ref) {

    final fcm = ref.watch(fcmProvider);

    // Set alarms when alarm schedule updates
    ref.listen<AsyncValue<List<AlarmInfo>>>(
      alarmScheduleProvider,
      (prev, next) {
        final prevData = prev?.valueOrNull;
        final nextData = next.valueOrNull;

        if (prevData != null && nextData != null) {
          if (prevData.length == nextData.length &&
              prevData.every((e) => nextData.any((n) =>
                n.id == e.id &&
                n.alarm == e.alarm))) {
            return;
          }
        }

        if (nextData == null) return;

        alarmRunner(() async {
          final now = DateTime.now().toUtc();
          await Alarm.stopAll();

          final vibratePref = ref.read(vibratePrefProvider);

          // set one alarm for each round
          for (final (index, (id: _, :name, :alarm, :player)) in nextData.indexed) {
            if (now.isBefore(alarm)) {
              final title = '$name starts in 5 minutes';
              final body = player != null
                  ? '${player.name} is at table ${player.table}'
                  : '';
              await setAlarm(alarm, title, body, index + 1, vibratePref);
            }
          }
        });
      },
    );

    // Update firebase subscription when tournamentId changes
    ref.listen(
      tournamentIdProvider,
      (prev, next) {
        if (prev case TournamentId tournamentId) {
          fcm.unsubscribeFromTopic(tournamentId);
          fcm.unsubscribeFromTopic('$tournamentId-');
        }
        if (next case TournamentId tournamentId) {
          fcm.subscribeToTopic(tournamentId);
          fcm.subscribeToTopic('$tournamentId-');
        }
      },
    );

    // Update firebase subscription when tournamentId or playerId changes
    ref.listen(
      tournamentPlayerIdProvider,
      (prev, next) {
        if (prev case (:TournamentId tournamentId, :PlayerId playerId)) {
          fcm.unsubscribeFromTopic('$tournamentId-$playerId');
          fcm.subscribeToTopic('$tournamentId-');
        }
        if (next case (:TournamentId tournamentId, :PlayerId playerId)) {
          fcm.unsubscribeFromTopic('$tournamentId-');
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

    final lightTheme = ThemeData.light(useMaterial3: true);
    final darkTheme = ThemeData.dark(useMaterial3: true);
    return FGBGNotifier(
      onEvent: (event) async {
        if (event != FGBGType.foreground) return;
        checkAlarms();
      },
      child: MaterialApp(
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
      ),
    );
  }
}

final initialTabProvider = StateProvider<TournamentTab?>((ref) => null);

Future<void> initPermissions() async {
  final status = await Permission.scheduleExactAlarm.status;
  if (status.isDenied) {
    await Permission.scheduleExactAlarm.request();
  }
}

// TODO we should maybe do this on app init too
void checkAlarms() async {
  final ringStream = await Alarm.getAlarms();
  for (final settings in ringStream) {
    // we'll give ourselves a 3s buffer to avoid a weird race condition
    if (DateTime.now().isAfter(
        settings.dateTime.subtract(Duration(seconds: 3)))) {
      final isRinging = await Alarm.isRinging(settings.id);
      if (isRinging) {
        Log.debug('open alarm page on FG');
        openAlarmPage(settings);
        break;
      }
    }
  }
}
