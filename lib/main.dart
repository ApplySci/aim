// native imports
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// third-party imports
import 'package:alarm/alarm.dart';
import 'package:flutter_redux/flutter_redux.dart';

// app imports
import 'db.dart';
import 'fcm_client.dart';
import 'home.dart';
import 'info.dart';
import 'player_list.dart';
import 'score_table.dart';
import 'seats.dart';
import 'settings.dart';
import 'store.dart';
import 'tournaments.dart';
import 'utils.dart';

Future main() async {
  // do this before everything
  WidgetsFlutterBinding.ensureInitialized();

  await initPrefs();
  await setupFCM();
  DB.instance.getTournamentFromId(prefs.getString('tournamentId') ?? '');
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.black, //top bar color
    statusBarIconBrightness: Brightness.light, //top bar icons
    systemNavigationBarColor: Colors.black, //bottom bar color
    systemNavigationBarIconBrightness: Brightness.light, //bottom bar icons
  ));
  await Alarm.init();

  DB.instance.getTournaments();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreProvider<AllState>(
      store: store,
      child: MaterialApp(
        initialRoute: ROUTES.home,
        scaffoldMessengerKey: DB.instance.scaffoldMessengerKey,
        title: 'All-Ireland Mahjong Tournaments',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
          useMaterial3: true,
        ),
        routes: {
          ROUTES.home: (context) => const MyHomePage(),
          ROUTES.info: (context) => const TournamentInfo(),
          ROUTES.seating: (context) => const Seating(),
          ROUTES.players: (context) => const Players(),
          ROUTES.settings: (context) => const SettingsScreen(),
          ROUTES.tournaments: (context) => const Tournaments(),
          ROUTES.scoreTable: (context) => const ScoreTable(),
          // ROUTES.privacyPolicy: (context) => const (),
        },
      ),
    );
  }
}
