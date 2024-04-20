import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'frame.dart';
import 'store.dart';

class TournamentInfo extends StatelessWidget {
  const TournamentInfo({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return {
          'name': store.state.tournamentName,
          'address': store.state.tournamentAddress,
          'playerMap': store.state.playerMap,
          'rounds': store.state.roundDone,
          'selected': store.state.selected,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> s) {
        return navFrame(
          context,
          Column(children: [
            Row(children: [const Icon(Icons.location_on), Text(s['address'])]),
          ]),
        );
      },
    );
  }
}
