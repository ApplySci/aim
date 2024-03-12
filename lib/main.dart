// native imports
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// third-party imports
import 'package:flutter_redux/flutter_redux.dart';
import 'package:firebase_core/firebase_core.dart';

// app imports
import 'firebase_options.dart';
import 'notifications.dart';
import 'player_list.dart';
import 'score_table.dart';
import 'store.dart';
import 'utils.dart';

Future main() async {
  // do this before everything
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.black, //top bar color
    statusBarIconBrightness: Brightness.light, //top bar icons
    systemNavigationBarColor: Colors.black, //bottom bar color
    systemNavigationBarIconBrightness: Brightness.light, //bottom bar icons
  ));

  await initPrefs();
  await setNotifierEvents();
  setupInteractedMessage(); // Handle any messages that caused the terminated app to re-open
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'All-Ireland Mahjong Tournaments',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'All-Ireland Mahjong Tournaments'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return StoreProvider<AllState>(
      // Pass the store to the StoreProvider. Any ancestor `StoreConnector`
      // Widgets will find and use this value as the `Store`.
      store: store,
      child: StoreConnector<AllState, String>(
        converter: (store) => store.state.preferences['backgroundColour'],
        builder: (BuildContext context, String color) {
          return Scaffold(
            // TODO MaterialApp(
            appBar: AppBar(
              backgroundColor: Theme.of(context).colorScheme.inversePrimary,
              title: Text(widget.title),
            ),
            body: SingleChildScrollView(
              scrollDirection: Axis.vertical,
              child: Column(
                children: [
                  ElevatedButton(
                    onPressed: () => store.dispatch(STORE.setScores),
                    child: const Text('update'),
                  ),
                  const Players(),
                  /*
                  const SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: ScoreTable(),
                  ),
                  */
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
