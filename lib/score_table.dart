import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'package:data_table_2/data_table_2.dart';

import 'score_cell.dart';
import 'store.dart';


class ScoreTable extends StatelessWidget {
  ScoreTable();

  void onTap() {}

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
          DataColumn2(
            label: Text(''),
            size: ColumnSize.S,
          ),
          DataColumn2(
            label: Text('Player'),
            size: ColumnSize.L,
          ),
          DataColumn(label: Text('Total')),
        ];
        for (var i = rounds; i > 0; i--) {
          columns.add(
            DataColumn2(
              label: Text("R${i}"),
              size: ColumnSize.S,
            ),
          );
        }
        List<DataRow2> rows = <DataRow2>[];
        int pos = 0;
        for (final score in storeValues['scores']) {
          List<DataCell> row = [
            DataCell(Text(pos.toString())),
            DataCell(Text(score['name'])),
            ScoreCell(score['total'], onTap),
          ];
          for (var i = rounds; i > 0; i--) {
            row.add(ScoreCell(score['roundScores'][i - 1], onTap));
          }
          rows.add(DataRow2(cells: row));
          pos++;
        }
        return DataTable2(
          columns: columns,
          rows: rows,
        );
      },
    );
  }

}
