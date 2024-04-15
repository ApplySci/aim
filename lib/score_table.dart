import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'frame.dart';
import 'score_cell.dart';
import 'store.dart';
import 'utils.dart';

class ScoreTable extends StatelessWidget {
  const ScoreTable({super.key});

  void onTap() {
    // TODO write this function to go to an individual player's summary or something
  }

  final Widget _verticalDivider = const VerticalDivider(
    color: Color(0xff999999),
    thickness: 1,
  );

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return {
          'scores': store.state.scores,
          'playerMap': store.state.playerMap,
          'rounds': store.state.roundDone,
          'selected': store.state.selected,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> s) {
        /*
        TODO 2) are we even handling penalties properly? Are they where we expect them?
        TODO 3) Are the round orders in the order we expect, or in the reverse of what we expect?
         */
        int rounds = s['rounds'];
        List<DataColumn> columns = <DataColumn>[
          const DataColumn(
            label: Text(''),
            numeric: true,
          ),
          const DataColumn(
            label: Text('Player'),
          ),
          const DataColumn(
            label: Text('Total'),
            numeric: true,
          ),
          DataColumn(label: _verticalDivider),
        ];
        for (int i = rounds; i > 0; i--) {
          columns.add(
            DataColumn(
              label: Text("R$i"),
              numeric: true,
            ),
          );
        }
        columns.add(const DataColumn(
          label: Text("Pen."),
          numeric: true,
        ));
        List<DataRow> rows = <DataRow>[];
        bool shade = false;

        // create one table row for each player

        for (final score in s['scores']) {
          List<DataCell> row = [
            DataCell(Text(score['r'])),
            DataCell(ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 150),
              child: Text(s['playerMap'][score['id']]),
            )),
            ScoreCell(score['t'], onTap),
            DataCell(_verticalDivider),
          ];
          for (int i = min(rounds, score['s'].length - 1); i > 0; i--) {
            row.add(ScoreCell(score['s'][i-1], onTap));
          }
          row.add(ScoreCell(score['p'], null));
          bool highlight = s['selected'] == score['id'];

          MaterialStateProperty<Color>? rowColour = highlight
              ? MaterialStateProperty.all<Color>(selectedHighlight)
              : (shade
              ? MaterialStateProperty.all<Color>(const Color(0x22ffffcc))
              : null);

          rows.add(DataRow(
            color: rowColour,
            cells: row,
          ));
          shade = !shade;
        }

        return Frame(
          context,
          SingleChildScrollView(
            scrollDirection: Axis.vertical,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: rows.isEmpty ? const Text('no data yet') :
                DataTable(
                columns: columns,
                rows: rows,
                columnSpacing: 10,
              ),
            ),
          ),
        );
      },
    );
  }
}
