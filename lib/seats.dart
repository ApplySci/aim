import 'package:aim_tournaments/defaults.dart';
import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'store.dart';
import 'utils.dart';

class Seating extends StatefulWidget {
  const Seating({super.key});

  @override
  State<Seating> createState() => _SeatingState();
}

class _SeatingState extends State<Seating> {
  bool showAll = false;

  void toggleShowAll(yes) => setState(() => showAll = yes);

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return {
          'seating': store.state.seating,
          'selected': store.state.selected,
          'thisSeating': store.state.theseSeats,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> s) {
        bool haveSelection = s['selected'] >= 0;
        List seats = s[haveSelection && !showAll ? 'thisSeating' : 'seating'];
        List<Widget> allHanchan = [];
        for (int h = 0; h < seats.length; h++) {
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
              Text(' ${HANCHAN_NAMES[h]}'),
              // TODO add hanchan start time here
            ],
          ));
          allHanchan.add(const SizedBox(height: 5));
          for (int t = 0; t < seats[h].length; t++) {
            allHanchan.add(Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.table_restaurant),
                Text(' ${TABLE_NAMES[t]}'),
              ],
            ));
            allHanchan.add(AssignedTable(seats[h][t]));
            allHanchan.add(const SizedBox(height: 10));
          }
          // TODO add a divider here
        }
        return Column(children: [
          const Text('Show all seating, or just the selected player?'),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Selected'),
              SwitchToggle(haveSelection, toggleShowAll),
              const Text('All'),
            ],
          ),
          SingleChildScrollView(
            child: Column(
              children: allHanchan,
            ),
          ),
        ]);
      },
    );
  }
}

class AssignedTable extends StatefulWidget {
  final List<int> seats; // E,S,N,W player indices
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
      for (var i = 0; i < widget.seats.length; i++) {
        rows.add(DataRow(cells: [
          DataCell(Text(winds[i])),
          DataCell(Container(
            color: widget.seats[i] == s['selected']
                ? Colors.greenAccent
                : Colors.transparent,
            child: Text(s['players'][widget.seats[i]]),
          )),
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

class SwitchToggle extends StatefulWidget {
  final bool live;
  final void Function(bool) callback;

  const SwitchToggle(this.live, this.callback, {super.key});

  @override
  State<SwitchToggle> createState() => _SwitchToggleState();
}

class _SwitchToggleState extends State<SwitchToggle> {
  bool light = true;

  void switchIt(bool value) {
    widget.callback(value);
    setState(() {
      light = value;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Switch(
      // This bool value toggles the switch.
      value: light,
      activeColor: Colors.red,
      onChanged: widget.live ? switchIt : null,
    );
  }
}
