import 'package:collection/collection.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '/providers.dart';
import '/utils.dart';

final negSignProvider = Provider((ref) {
  final japaneseNumbers = ref.watch(japaneseNumbersProvider);
  return japaneseNumbers ? '▲' : '-';
});

class ScoreTable extends ConsumerWidget {
  const ScoreTable({super.key});

  void onTap(BuildContext context, int playerId) {}

  @override
  Widget build(context, ref) {
    final negSign = ref.watch(negSignProvider);
    final selectedPlayerId = ref.watch(selectedPlayerIdProvider);
    final playerScores = ref.watch(playerScoreListProvider);
    final rounds = ref.watch(roundsProvider);
    return playerScores.when(
      skipLoadingOnReload: true,
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => Center(child: Text('$error')),
      data: (playerScores) {
        final selectedScore = playerScores.firstWhereOrNull(
          (e) => e.id == selectedPlayerId,
        );
        return DataTable2(
          fixedTopRows: selectedPlayerId != null ? 2 : 1,
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
            for (int i = rounds - 1; i >= 0; i--)
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
                negSign: negSign,
                rounds: rounds,
                onTap: () => onTap(context, selectedScore.id),
                color: WidgetStateProperty.all<Color>(selectedHighlight),
              ),
            for (final score in playerScores)
              ScoreRow(
                selected: selectedPlayerId == score.id,
                score: score,
                negSign: negSign,
                rounds: rounds,
                onTap: () => onTap(context, score.id),
                color: selectedPlayerId == score.id
                    ? WidgetStateProperty.all<Color>(selectedHighlight)
                    : null,
              ),
          ],
          columnSpacing: 10,
        );
      },
    );
  }
}

class ScoreRow extends DataRow2 {
  ScoreRow({
    required PlayerScore score,
    required String negSign,
    required int rounds,
    required super.onTap,
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
          )),
          for (int i = rounds - 1; i >= 0; i--)
            DataCell(Score(
              score: score.roundScores.elementAtOrNull(i)?.score ?? 0,
              negSign: negSign,
            )),
          DataCell(Score(
            score: score.penalty,
            negSign: negSign,
          )),
        ]);
}

class Score extends StatelessWidget {
  const Score({
    super.key,
    required this.score,
    required this.negSign,
  });

  final int score;
  final String negSign;

  @override
  Widget build(BuildContext context) {
    return InkWell(
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
