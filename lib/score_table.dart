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
          'playerMap': store.state.playerMap,
          'rounds': store.state.rounds,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> s) {
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
        int pos = 1;
        bool shade = false;
        for (final score in s['scores']) {
          List<DataCell> row = [
            DataCell(Text(pos.toString())),
            DataCell(ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 150),
              child: Text(s['playerMap'][score['id']]),
            )),
            ScoreCell(score['total'], onTap),
            DataCell(_verticalDivider),
          ];
          for (int i = rounds; i >= 0; i--) {
            row.add(ScoreCell(score['roundScores'][i], onTap));
          }
          rows.add(DataRow(
            color: shade
                ? MaterialStateProperty.all<Color>(const Color(0x22ffffcc))
                : null,
            cells: row,
          ));
          pos++;
          shade = !shade;
        }
        return Frame(
          context,
          SingleChildScrollView(
            scrollDirection: Axis.vertical,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
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
