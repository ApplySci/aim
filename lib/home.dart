import 'package:flutter/material.dart';

// third-party imports
import 'package:flutter_redux/flutter_redux.dart';

// app imports
import 'client.dart';
import 'frame.dart';
import 'store.dart';
import 'tournaments.dart';

void _updateStore() {
  IO.getPlayers();
  IO.getSeating();
  IO.getScores();
}

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
            const Column(
              children: [
                ElevatedButton(
                  onPressed: _updateStore,
                  child: Text('update'),
                ),
                Text('Pick a tournament to follow'),
                TournamentList(),
              ],
            ),
          );
        },
      ),
    );
  }
}
