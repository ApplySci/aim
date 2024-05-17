// native imports
import 'dart:async';

import 'package:alarm/model/alarm_settings.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// third-party imports
import 'package:alarm/alarm.dart';
import 'package:flutter_redux/flutter_redux.dart';

// app imports
import 'alarm.dart';
import 'db.dart';
import 'fcm_client.dart';
import 'home.dart';
import 'settings.dart';
import 'store.dart';
import 'tournament.dart';
import 'tournaments.dart';
import 'utils.dart';

Future main() async {
  WidgetsFlutterBinding.ensureInitialized(); // do this before everything

  await initPrefs();
  await setupFCM();
  await Alarm.init();
  DB.instance.getTournaments();
  DB.instance.getTournamentFromId(prefs.getString('tournamentId') ?? '');
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.black, //top bar color
    statusBarIconBrightness: Brightness.light, //top bar icons
    systemNavigationBarColor: Colors.black, //bottom bar color
    systemNavigationBarIconBrightness: Brightness.light, //bottom bar icons
  ));
  runApp(_MyApp());
}

class _MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<_MyApp> {
  late StreamSubscription<AlarmSettings> alarmListener;

  @override
  void initState() {
    super.initState();

    alarmListener = Alarm.ringStream.stream.listen(alarmIsRinging);
  }

  // Unhandled Exception: Looking up a deactivated widget's ancestor is unsafe.
  // E/flutter ( 5008): At this point the state of the widget's element tree is no longer stable.
  Future<void> alarmIsRinging(AlarmSettings settings) async {
    await globalNavigatorKey.currentState?.push(
      MaterialPageRoute<void>(
        builder: (context) => AlarmScreen(settings: settings),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return StoreProvider<AllState>(
      store: store,
      child: MaterialApp(
        debugShowCheckedModeBanner:false,
        initialRoute: ROUTES.home,
        navigatorKey: globalNavigatorKey,
        scaffoldMessengerKey: DB.instance.scaffoldMessengerKey,
        title: 'All-Ireland Mahjong Tournaments',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
          useMaterial3: true,
        ),
        routes: {
          ROUTES.home: (context) => const MyHomePage(),
          ROUTES.settings: (context) => const SettingsScreen(),
          ROUTES.tournaments: (context) => const Tournaments(),
          ROUTES.tournament: (context) => const TournamentPage(),
        },
      ),
    );
  }
}
