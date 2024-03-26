import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'frame.dart';
import 'store.dart';
import 'utils.dart';

class Seating extends StatefulWidget {
  const Seating({super.key});

  @override
  State<Seating> createState() => _SeatingState();
}

class _SeatingState extends State<Seating> {
  bool showAll = false;

  void toggleShowAll(bool yes) => setState(() => showAll = yes);

  List<Widget> getHanchan(SeatingPlan seats, int roundDone) {
    List<Widget> allHanchan = [];
    int roundCount = 0;
    for (final Map round in seats) {
      roundCount++;
      if (roundCount <= roundDone) continue; // skip rounds if they're over
      allHanchan.add(Container(
        height: 10,
        margin: const EdgeInsets.all(15.0),
        padding: const EdgeInsets.all(10.0),
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(
              width: 3,
              color: Colors.blueAccent,
            ),
          ),
        ),
      ));
      allHanchan.add(Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.watch_later_outlined),
          Text(" ${round['id']} begins at ${round['start']}"),
        ],
      ));
      allHanchan.add(const SizedBox(height: 5));
      (round['tables'] as Map<String, dynamic>)
          .forEach((String tableName, dynamic plan) {
        allHanchan.add(Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.table_restaurant),
            Text(' $tableName'),
          ],
        ));
        allHanchan.add(AssignedTable(plan));
        allHanchan.add(const SizedBox(height: 10));
      });
    }
    return allHanchan;
  }

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return {
          'roundDone': store.state.roundDone,
          'scores': store.state.scores,
          'seating': store.state.seating,
          'selected': store.state.selected,
          'thisSeating': store.state.theseSeats,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> s) {
        bool haveSelection = s['selected'] >= 0;
        SeatingPlan seats =
            s[haveSelection && !showAll ? 'thisSeating' : 'seating'];
        if (seats.isEmpty) {
          return Frame(context,
              const Center(child: Text('No seating schedule available')));
        }

        List<Widget> rows = [];
        if (haveSelection) {
          rows.add(
              const Text('Show all seating, or just the selected player?'));

          rows.add(
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('Selected'),
                Switch(
                  value: showAll,
                  activeColor: Colors.red,
                  onChanged: haveSelection ? toggleShowAll : null,
                ),
                const Text('All'),
              ],
            ),
          );
        }
        rows.addAll(getHanchan(seats, s['roundDone']));
        return Frame(
            context, SingleChildScrollView(child: Column(children: rows)));
      },
    );
  }
}

class AssignedTable extends StatefulWidget {
  final List seats; // E,S,N,W player indices
  const AssignedTable(
    this.seats, {
    super.key,
  });

  @override
  State<AssignedTable> createState() => _AssignedTableState();
}

class _AssignedTableState extends State<AssignedTable> {
  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(converter: (store) {
      return {
        'players': store.state.playerMap,
        'selected': store.state.selected,
        'winds': store.state.preferences['japaneseWinds'],
      };
    }, builder: (BuildContext context, Map<String, dynamic> s) {
      List<DataRow> rows = <DataRow>[];
      String winds = WINDS[s['winds'] ? 'japanese' : 'western'].toString();
      for (int i = 0; i < min(4, widget.seats.length); i++) {
        rows.add(DataRow(
            color: MaterialStateProperty.all<Color>(
                widget.seats[i] == s['selected']
                ? selectedHighlight
                : Colors.transparent),
            cells: [
          DataCell(Text(winds[i])),
          DataCell(Text(s['players'][widget.seats[i]])),
        ]));
      }
      return DataTable(
        border: TableBorder.symmetric(
          inside: BorderSide.none,
          outside: const BorderSide(width: 2, color: Color(0x88888888)),
        ),
        headingRowHeight: 0,
        columns: [
          DataColumn(label: Container()),
          DataColumn(label: Container()),
        ],
        rows: rows,
        columnSpacing: 10,
      );
    });
  }
}
