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
        // TODO iterate over hanchan

/*
const List<String> HANCHAN_NAMES = ['R1', 'R2', 'R3'];
const List<String> TABLE_NAMES = ['alef', 'bet'];
const List<List<List<int>>> SEATING = [
  [ [1,2,3,4,], [5,6,7,8,], ],
  [ [2,4,6,8,], [1,3,5,7,], ],
  [ [3,4,1,6,], [2,7,8,5,], ],
];
*/
        List<Widget> allHanchan = [
          ListTile(title: Text('Item 1')),
        ];
        return Column(children: [
          const Text('Show all seating, or just the selected player?'),
          Row(
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
  final String hanchanName;
  final String tableName;
  final List<int> seats; // E,S,N,W player indices
  final String startTime;

  const AssignedTable(
    this.hanchanName,
    this.tableName,
    this.startTime,
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
        'players': store.state.players,
        'selected': store.state.preferences['playerId'],
        'winds': store.state.preferences['japaneseWinds'],
      };
    }, builder: (BuildContext context, Map<String, dynamic> s) {
      List<DataRow> rows = <DataRow>[];
      String winds = WINDS[s['winds'] ? 'japanese' : 'western'].toString();
      for (var i = 0; i < 4; i++) {
        rows.add(DataRow(cells: [
          DataCell(Text(winds[i])),
          DataCell(Container(
            color: widget.seats[i] == s['selected']
                ? Colors.greenAccent
                : Colors.amber[600],
            child: Text(s['players'][widget.seats[i]].name),
          )),
        ]));
      }
      return Card(
          child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              const Icon(Icons.table_restaurant),
              Text('${widget.hanchanName} - Table ${widget.tableName}'),
            ],
          ),
          DataTable(
            headingRowHeight: 0,
            columns: [
              DataColumn(label: Container()),
              DataColumn(label: Container()),
            ],
            rows: rows,
            columnSpacing: 10,
          ),
        ],
      ));
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
