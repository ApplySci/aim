import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'store.dart';
import 'utils.dart';

class Seating extends StatelessWidget {
  const Seating({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return {
          'seating': store.state.seating,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> storeValues) {
        // List seats = storeValues['seating'];
        // TODO iterate over hanchan
        return const Text('yo');
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
            color: widget.seats[i] == s['selected'] ? Colors.greenAccent : Colors.amber[600],
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
