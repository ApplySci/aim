import 'package:flutter/material.dart';

// third-party imports
import 'package:flutter_redux/flutter_redux.dart';

// app imports
import 'frame.dart';
import 'store.dart';
import 'tournaments.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return StoreProvider<AllState>(
      store: store,
      child: StoreConnector<AllState, String>(
        converter: (store) => store.state.preferences['backgroundColour'],
        builder: (BuildContext context, String color) {
          return Frame(
            context,
            const TournamentList(),
          );
        },
      ),
    );
  }
}
