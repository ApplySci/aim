import 'package:flutter/material.dart';

// third-party imports
import 'package:flutter_redux/flutter_redux.dart';

// app imports
import 'client.dart';
import 'frame.dart';
import 'store.dart';
import 'utils.dart';

void _updateStore() {
  IO.getPlayers((List<Player> players) {
    store.dispatch({
      'type': STORE.setPlayerList,
      'players': players,
    });
  });

  IO.getSeating((Map<String, dynamic> seating) {
    store.dispatch({
      'type': STORE.setSeating,
      'seating': seating,
    });
  });


  IO.getScores((List<Map<String,dynamic>> scores) {
    store.dispatch({
      'type': STORE.setScores,
      'scores': scores,
    });
  });

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
            const SingleChildScrollView(
              scrollDirection: Axis.vertical,
              child: Column(
                children: [
                  ElevatedButton(
                    onPressed: _updateStore,
                    child: Text('update'),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
