import 'package:collection/collection.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'package:intl/intl.dart';

import 'store.dart';
import 'utils.dart';

class PlayerScore extends ScoreState {
  const PlayerScore({
    required super.id,
    required this.name,
    required super.rank,
    required super.total,
    required super.penalty,
    required super.roundScores,
    required super.roundDone,
  });

  final String name;

  @override
  List<Object?> get props => [
        ...super.props,
        name,
      ];
}

List<PlayerScore> toPlayerScoreList(
  List<ScoreState> scores,
  List<Player> players,
) {
  final Map<int, String> playerNames =
      Map.fromEntries(players.map((e) => MapEntry(e.id, e.name)));

  return scores
      .map((e) => PlayerScore(
            id: e.id,
            name: playerNames[e.id]!,
            rank: e.rank,
            total: e.total,
            penalty: e.penalty,
            roundScores: e.roundScores,
            roundDone: e.roundDone,
          ))
      .toList();
}

typedef ScoreTableState = ({
  String negSign,
  List<PlayerScore> scores,
  int rounds,
  int? selected,
});

class ScoreTable extends StatelessWidget {
  const ScoreTable({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, ScoreTableState>(
      distinct: true,
      converter: (store) {
        final japaneseNumbers = prefs.getBool('japaneseNumbers') ?? false;
        return (
          negSign: japaneseNumbers ? '▲' : '-',
          scores: toPlayerScoreList(store.state.scores, store.state.players),
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
    final selectedScore =
        state.scores.firstWhereOrNull((e) => e.id == state.selected);
    return DataTable2(
      fixedTopRows: selectedScore != null ? 2 : 1,
      columns: [
        const DataColumn2(
          label: Text(''),
          numeric: true,
          fixedWidth: 24,
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
        if (selectedScore case PlayerScore score)
          ScoreRow(
            selected: true,
            score: score,
            negSign: state.negSign,
            rounds: state.rounds,
            onTap: onTap,
            color: WidgetStateProperty.all<Color>(selectedHighlight),
          ),
        for (final (index, score) in state.scores.indexed)
          ScoreRow(
            selected: state.selected == score.id,
            score: score,
            negSign: state.negSign,
            rounds: state.rounds,
            onTap: onTap,
            color: state.selected == score.id
                ? WidgetStateProperty.all<Color>(selectedHighlight)
                : index.isEven
                    ? WidgetStateProperty.all<Color>(const Color(0x22ffffcc))
                    : null,
          ),
      ],
      columnSpacing: 10,
    );
  }
}

class ScoreRow extends DataRow2 {
  ScoreRow({
    required PlayerScore score,
    required String negSign,
    required int rounds,
    required void Function() onTap,
    super.color,
    super.selected,
  }) : super(cells: [
          DataCell(Text(score.rank)),
          DataCell(Text(
            score.name,
            softWrap: false,
            overflow: TextOverflow.ellipsis,
          )),
          DataCell(Score(
            score: score.total,
            negSign: negSign,
            onTap: onTap,
          )),
          for (int i = rounds - 1; i >= 0; i--)
            DataCell(Score(
              score: score.roundScores[i],
              negSign: negSign,
              onTap: onTap,
            )),
          DataCell(Score(
            score: score.penalty,
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
