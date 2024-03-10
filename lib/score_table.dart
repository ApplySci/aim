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
        List<DataColumn2> columns = <DataColumn2>[
          DataColumn2(
            size: ColumnSize.S,
            label: Text(''),
            numeric: true,
          ),
          DataColumn2(
            size: ColumnSize.L,
            label: Text('Player'),
          ),
          DataColumn2(
            size: ColumnSize.M,
            label: Text('Total'),
            numeric: true,
          ),
        ];
        for (var i = rounds; i > 0; i--) {
          columns.add(
            DataColumn2(
              size: ColumnSize.M,
              label: Text("R${i}"),
              numeric: true,
            ),
          );
        }
        columns.add(DataColumn2(
          size: ColumnSize.M,
          label: Text("Pen."),
          numeric: true,
        ));
        List<DataRow2> rows = <DataRow2>[];
        int pos = 1;
        for (final score in storeValues['scores']) {
          List<DataCell> row = [
            DataCell(Text(pos.toString())),
            DataCell(Text(score['name'])),
            ScoreCell(score['total'], onTap),
          ];
          for (var i = rounds; i >= 0; i--) {
            row.add(
              ScoreCell(score['roundScores'][i], onTap)
            );
          }
          rows.add(DataRow2(cells: row));
          pos++;
        }
        return DataTable2(
          columns: columns,
          rows: rows,
          columnSpacing: 10,
          fixedLeftColumns: 2,
          fixedTopRows: 4,
          lmRatio: 2,
          smRatio: 0.5,
        );
      },
    );
  }

}
