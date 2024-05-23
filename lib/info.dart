import 'package:intl/intl.dart';
import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'store.dart';
import 'utils.dart';
import 'venue.dart';

typedef TournamentInfoState = ({
  TournamentState tournament,
  ScheduleState schedule,
});

class TournamentInfo extends StatelessWidget {
  const TournamentInfo({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, TournamentInfoState?>(
      distinct: true,
      converter: (store) =>
          store.state.tournament != null && store.state.schedule != null
              ? (
                  tournament: store.state.tournament!,
                  schedule: store.state.schedule!,
                )
              : null,
      builder: (context, state) {
        if (state == null) {
          return const Center(child: CircularProgressIndicator());
        }

        return ListView(
          children: [
            ListTile(
              leading: const Icon(Icons.location_on),
              title: Text(state.tournament.address),
              visualDensity: VisualDensity.compact,
              onTap: () => openMap(context, state.tournament.address),
              selected: true,
            ),
            ListTile(
              leading: const Icon(Icons.calendar_month),
              title: Text(dateRange(
                state.tournament.startDate,
                state.tournament.endDate,
              )),
              visualDensity: VisualDensity.compact,
            ),
            const ListTile(
              leading: Icon(Icons.table_restaurant),
              title: Text('Hanchan timings'),
              visualDensity: VisualDensity.compact,
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Table(
                border: TableBorder.all(
                  width: 2,
                  color: const Color(0x88888888),
                ),
                columnWidths: const {
                  0: IntrinsicColumnWidth(),
                  1: FlexColumnWidth(),
                },
                children: [
                  const TableRow(children: [
                    Padding(
                      padding: EdgeInsets.all(8),
                      child: Text(
                        'Round',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                    Padding(
                      padding: EdgeInsets.all(8),
                      child: Text(
                        'Starts At',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ]),
                  for (final schedule in state.schedule.rounds.values)
                    TableRow(children: [
                      Padding(
                        padding: const EdgeInsets.all(8),
                        child: Text(schedule.name),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8),
                        child: Text(DateFormat('EEEE d MMMM HH:mm')
                            .format(schedule.start)),
                      ),
                    ]),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}
