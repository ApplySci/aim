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
        return store.state.tournament;
      },
      builder: (BuildContext context, Map<String, dynamic> t) {
        return navFrame(
          context,
          Column(children: [
            Row(children: [const Icon(Icons.location_on), Text(t['address'])]),
          ]),
        );
      },
    );
  }
}
