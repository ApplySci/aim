import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'package:data_table_2/data_table_2.dart';

import 'score_cell.dart';
import 'store.dart';

class PlayerStatus {
  List<int> roundScores = <int>[].toList(growable: true);
  String name = 'unassigned';
  int totalScore = 0;
}

class ScoreTable extends StatelessWidget {
  ScoreTable();

  void onTap() {}

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return {
          'scores': store.state.scores,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> storeValues) {
        int rounds = storeValues['scores'][0].roundScores.length;
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
        return DataTable2(
          columns: columns,
          rows: storeValues['scores'].map((score) {
            List<DataCell> row = [
              DataCell(score.name),
              ScoreCell(score.totalScore, onTap),
            ];
            for (var i = rounds; i > 0; i--) {
              row.add(ScoreCell(score.roundScores[i - 1], onTap));
            }
            return DataRow2(cells: row);
          }).toList(),
        );
      },
    );
  }

}
