import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'frame.dart';
import 'store.dart';
import 'utils.dart';

class TournamentInfo extends StatelessWidget {
  const TournamentInfo({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return store.state.tournament;
      },
      builder: (BuildContext context, Map<String, dynamic> t) {

        DataTable timings;

        return navFrame(
          context,
          Column(children: [
            const SizedBox(height: 20),
            Row(children: [
              const SizedBox(width: 5),
              const Icon(Icons.location_on),
              Text(t['address'] ?? ''),
            ]),
            const SizedBox(height: 20),
            Row(children: [
              const SizedBox(width: 5),
              const Icon(Icons.calendar_month),
              Text(dateRange(t['start_date'], t['end_date'])),
            ]),
            const SizedBox(height: 20),
            const Row(children: [
              SizedBox(width: 5),
              Icon(Icons.table_restaurant),
              Icon(Icons.watch_later_outlined),
              Text('Hanchan timings'),
            ]),
            //timings,
          ]),
        );
      },
    );
  }
}
