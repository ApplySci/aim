import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'frame.dart';
import 'score_cell.dart';
import 'store.dart';

class ScoreTable extends StatelessWidget {
  const ScoreTable({super.key});

  void onTap() {}

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
          'rounds': store.state.rounds,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> storeValues) {
        int rounds = storeValues['rounds'];
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
        for (var i = rounds; i > 0; i--) {
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
        int pos = 1;
        for (final score in storeValues['scores']) {
          List<DataCell> row = [
            DataCell(Text(pos.toString())),
            DataCell(ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 150),
              child: Text(score['name']),
            )),
            ScoreCell(score['total'], onTap),
            DataCell(_verticalDivider),
          ];
          for (var i = rounds; i >= 0; i--) {
            row.add(ScoreCell(score['roundScores'][i], onTap));
          }
          rows.add(DataRow(cells: row));
          pos++;
        }
        return Frame(
          context,
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: columns,
              rows: rows,
              columnSpacing: 10,
            ),
          ),
        );
      },
    );
  }
}
