import 'dart:async';
import 'dart:io' show Platform;
import 'dart:collection';
import 'dart:math' show min;

import 'package:alarm/alarm.dart';
import 'package:alarm/utils/alarm_set.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_fgbg/flutter_fgbg.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest_10y.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'providers/migration.dart';
import 'models.dart';
import 'providers.dart';
import 'services/notification_preferences.dart';
import 'utils.dart';
import 'views/alarm_page.dart';
import 'views/player/player_page.dart';
import 'views/round/round_page.dart';
import 'views/tournament_list_page.dart';
import 'views/tournament/tournament_page.dart';

StreamSubscription<AlarmSet>? ringSubscription;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Log.init();

  // Add a try-catch specifically for Firebase initialization to better log errors
  try {
    Log.debug('Initializing Firebase and FCM');
    await initFirebaseMessaging();
    Log.debug('Firebase and FCM initialization completed');
  } catch (e, stack) {
    Log.debug('Error during Firebase/FCM initialization: $e');
    Log.debug('Stack trace: $stack');
    // Continue app initialization even if Firebase fails
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
    ringSubscription = Alarm.ringing.listen((AlarmSet alarmSet) {
      for (final AlarmSettings alarm in alarmSet.alarms) {
        // TODO catch if multiple alarms, kill all except newest
        openAlarmPage(alarm);
      }
    });
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

class _MyApp extends ConsumerStatefulWidget {
  @override
  ConsumerState<_MyApp> createState() => _MyAppState();
}

class _MyAppState extends ConsumerState<_MyApp> {
  @override
  void initState() {
    super.initState();
    ref.read(migrationProvider).checkMigration(context);
    _ensureFcmInitialized();
  }

  @override
  Widget build(BuildContext context) {
    final fcm = ref.watch(fcmProvider);

    // Set alarms when alarm schedule updates
    ref.listen<AsyncValue<List<AlarmInfo>>>(
      alarmScheduleProvider,
      (prev, next) async {
        final prevData = prev?.valueOrNull;
        final nextData = next.valueOrNull;

        // Skip if the alarms are identical
        if (prevData != null &&
            nextData != null &&
            prevData.length == nextData.length &&
            prevData.every((prev) => nextData.any((next) =>
            prev.id == next.id &&
                prev.name == next.name &&
                prev.alarm == next.alarm &&
                prev.vibratePref == next.vibratePref &&
                prev.player?.id == next.player?.id &&
                prev.player?.name == next.player?.name &&
                prev.player?.table == next.player?.table
            ))) {
          return;
        }

        final now = DateTime.now().toUtc();
        Log.debug('stopping all alarms');

        try {
          await Alarm.stopAll();
        } catch (e) {
          Log.warn('exception when stopping all alarms');
        }

        if (nextData == null) return;

        // set one alarm for each round
        for (final (index, (id: _, :name, :alarm, :player, :vibratePref)) in nextData.indexed) {
          if (now.isBefore(alarm)) {
            final title = '$name starts in 5 minutes';
            final body = player != null
                ? '${player.name} is at table ${player.table}'
                : '';
            Log.debug('setting alarm: $title');
            await setAlarm(alarm, title, body, index + 1, vibratePref);
          }
        }
      },
    );

    // Update firebase subscription when tournamentId or playerId changes
    ref.listen(
      tournamentPlayerIdProvider,
      (prev, next) async {
        if (next case (:TournamentId tournamentId, :PlayerId playerId)) {
          final service = ref.read(notificationPreferencesProvider);
          await service.refreshSubscriptions();
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
        // Clean up old logs when app comes to foreground
        await Log.onAppResume();
      },
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        initialRoute: ROUTES.home,
        navigatorKey: globalNavigatorKey,
        onGenerateRoute: (settings) {
          return MaterialPageRoute(
            settings: settings,
            builder: (context) {
              return PopScope(
                canPop: false,
                onPopInvoked: (didPop) async {
                  if (didPop) return;

                  final navigator = Navigator.of(context);
                  if (navigator.canPop()) {
                    await navigator.maybePop();
                  } else {
                    if (context.mounted) {
                      await navigator.pushReplacementNamed(ROUTES.tournaments);
                    }
                  }
                },
                child: _buildRoute(settings),
              );
            },
          );
        },
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
      ),
    );
  }

  // Helper method to ensure FCM is properly initialized after restart
  Future<void> _ensureFcmInitialized() async {
    try {
      Log.debug('Running FCM initialization check on platform: ${Platform.operatingSystem}');
      final prefs = await SharedPreferences.getInstance();
      final needsInit = prefs.getBool('fcm_needs_init') ?? false;

      if (needsInit) {
        Log.debug('FCM needs re-initialization after reset');
        await prefs.setBool('fcm_needs_init', false);
        await initFirebaseMessaging();

        // Verify initialization was successful
        final verificationToken = await FirebaseMessaging.instance.getToken();
        Log.debug('FCM re-initialization ${verificationToken != null ? 'successful' : 'failed'}');
        return;
      }

      // Request a token to trigger any initialization that might have been missed
      final token = await FirebaseMessaging.instance.getToken();
      if (token != null) {
        Log.debug('FCM initialized with token: ${token.substring(0, min(10, token.length))}...');

        // Log topics if available
        final topics = prefs.getString('fcm_topics');
        Log.debug('Current FCM topics: $topics');
      } else {
        Log.debug('FCM token is null, attempting re-initialization');
        // Try to force re-initialization
        await initFirebaseMessaging();
      }
    } catch (e, stack) {
      Log.debug('Error verifying FCM initialization: $e');
      Log.debug('Stack trace: $stack');
    }
  }

  Widget _buildRoute(RouteSettings settings) {
    switch (settings.name) {
      case ROUTES.home:
      case ROUTES.tournaments:
        return const TournamentListPage();
      case ROUTES.tournament:
        return const TournamentPage();
      case ROUTES.player:
        return const PlayerPage();
      case ROUTES.round:
        return const RoundPage();
      default:
        return const TournamentListPage();
    }
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
