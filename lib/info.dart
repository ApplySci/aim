import 'package:intl/intl.dart';
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
        return {
          't': store.state.tournament,
          'sc': store.state.schedule,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> d) {

        List<DataRow> rows = [];
        d['sc'].forEach((key, value) {
          if (key != "timezone") {
            rows.add(DataRow(cells: [
              DataCell(Text(value['name'])),
              DataCell(Text(DateFormat('EEEE d MMMM HH:mm').format(
                  value['start']))),
            ]));
          }
        });

        return navFrame(
          context,
          Column(children: [
            const SizedBox(height: 20),
            Row(children: [
              const SizedBox(width: 5),
              const Icon(Icons.location_on),
              Text(d['t']['address'] ?? ''),
            ]),
            const SizedBox(height: 20),
            Row(children: [
              const SizedBox(width: 5),
              const Icon(Icons.calendar_month),
              Text(dateRange(d['t']['start_date'], d['t']['end_date'])),
            ]),
            const SizedBox(height: 20),
            const Row(children: [
              SizedBox(width: 5),
              Icon(Icons.table_restaurant),
              Icon(Icons.watch_later_outlined),
              Text('Hanchan timings'),
            ]),
            DataTable(
              columns: const [
                DataColumn(label: Text('round'),),
                DataColumn(label: Text('starts at'),)],
              rows: rows,
              columnSpacing: 10,
            ),
          ]),
        );
      },
    );
  }
}
