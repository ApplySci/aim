import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'package:intl/intl.dart';

import 'store.dart';
import 'utils.dart';

typedef ScoreTableState = ({
  String negSign,
  List<ScoreState> scores,
  Map<int, String> playerMap,
  int rounds,
  int? selected,
});

class ScoreTable extends StatelessWidget {
  const ScoreTable({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, ScoreTableState>(
      converter: (store) {
        bool japaneseNumbers = prefs.getBool('japaneseNumbers') ?? false;
        return (
          negSign: japaneseNumbers ? '▲' : '-',
          scores: store.state.scores,
          playerMap: store.state.playerMap,
          rounds: store.state.roundDone,
          selected: store.state.selected,
        );
      },
      builder: (context, state) => ScoreDataTable(state: state),
    );
  }
}

class ScoreDataTable extends StatelessWidget {
  const ScoreDataTable({
    super.key,
    required this.state,
  });

  final ScoreTableState state;

  void onTap() {
    // TODO write this function to go to an individual player's summary or something
  }

  @override
  Widget build(BuildContext context) {
    return DataTable2(
      minWidth: double.infinity,
      columns: [
        const DataColumn2(
          label: Text(''),
          numeric: true,
          fixedWidth: 28,
        ),
        const DataColumn2(
          label: Text('Player'),
          fixedWidth: 200,
        ),
        const DataColumn2(
          label: Text('Total'),
          numeric: true,
          fixedWidth: 60,
        ),
        for (int i = state.rounds - 1; i >= 0; i--)
          DataColumn2(
            label: Text('R$i'),
            numeric: true,
            fixedWidth: 60,
          ),
        const DataColumn2(
          label: Text('Pen.'),
          numeric: true,
          fixedWidth: 60,
        ),
      ],
      rows: [
        for (final (index, score) in state.scores.indexed)
          ScoreRow(
            score: score,
            player: state.playerMap[score.id]!,
            negSign: state.negSign,
            rounds: state.rounds,
            onTap: onTap,
            color: state.selected == score.id
                ? MaterialStateProperty.all<Color>(selectedHighlight)
                : index.isEven
                    ? MaterialStateProperty.all<Color>(const Color(0x22ffffcc))
                    : null,
          ),
      ],
      columnSpacing: 10,
    );
  }
}

class ScoreRow extends DataRow {
  ScoreRow({
    required ScoreState score,
    required String player,
    required String negSign,
    required int rounds,
    required void Function() onTap,
    super.color,
  }) : super(cells: [
          DataCell(Text(score.r)),
          DataCell(Text(
            player,
            softWrap: false,
            overflow: TextOverflow.ellipsis,
          )),
          DataCell(Score(
            score: score.t,
            negSign: negSign,
            onTap: onTap,
          )),
          for (int i = rounds - 1; i >= 0; i--)
            DataCell(Score(
              score: score.s[i],
              negSign: negSign,
              onTap: onTap,
            )),
          DataCell(Score(
            score: score.p,
            negSign: negSign,
            onTap: null,
          )),
        ]);
}

class Score extends StatelessWidget {
  const Score({
    super.key,
    required this.score,
    required this.negSign,
    required this.onTap,
  });

  final int score;
  final String negSign;
  final void Function()? onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Text(
        NumberFormat('+#0.0;$negSign#0.0').format(score / 10),
        // Display score with 1 decimal point
        style: TextStyle(
          color: Color(switch (score) {
            > 0 => 0xff00bb00,
            < 0 => 0xff660000,
            _ => 0xffbbbbbb,
          }),
          fontWeight: FontWeight.bold,
          fontSize: 16,
        ),
      ),
    );
  }
}
