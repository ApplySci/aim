import 'dart:math';

import 'package:collection/collection.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import '/providers.dart';
import '/utils.dart';
import '/views/score_text.dart';

const columnMargin = 18;

const scoreStyle = TextStyle(
  fontWeight: FontWeight.bold,
  fontSize: 16,
);

Size textSize(String text, {TextStyle? style}) {
  return (TextPainter(
    text: TextSpan(text: text, style: style),
    maxLines: 1,
    textDirection: TextDirection.ltr,
  )..layout())
      .size;
}

Size scoreSize(int score, String negSign) => textSize(
      // Display score with 1 decimal point
      scoreFormat(score, negSign),
      style: scoreStyle,
    );

final scoreWidthProvider = StreamProvider.autoDispose((ref) async* {
  final negSign = ref.watch(negSignProvider);
  final playerScores = await ref.watch(playerScoreListProvider.future);
  final maxRankWidth = playerScores
      .map((playerScore) => playerScore.rank)
      .map((rank) => textSize(rank).width)
      .max;
  final maxNameWidth = playerScores
      .map((playerScore) => playerScore.name)
      .map((name) => textSize(name).width)
      .max;
  final maxScoreWidth = playerScores
      .map((playerScore) => playerScore.roundScores.map((e) => e.score))
      .flattened
      .map((score) => scoreSize(score, negSign).width)
      .max;
  final maxTotalWidth = playerScores
      .map((playerScore) => playerScore.total)
      .map((score) => scoreSize(score, negSign).width)
      .max;
  final maxPenaltyWidth = playerScores
      .map((playerScore) => playerScore.penalty)
      .map((score) => scoreSize(score, negSign).width)
      .max;

  yield (
    playerScores: playerScores,
    maxRankWidth: maxRankWidth,
    maxNameWidth: maxNameWidth,
    maxScoreWidth: max(max(maxScoreWidth, maxTotalWidth), maxPenaltyWidth),
  );
});

class ScoreTable extends ConsumerWidget {
  const ScoreTable({super.key});

  void onTap(BuildContext context, PlayerId playerId) =>
      Navigator.of(context).pushNamed(ROUTES.player, arguments: playerId);

  @override
  Widget build(context, ref) {
    final selectedPlayerId = ref.watch(selectedPlayerIdProvider);
    final playerScores = ref.watch(scoreWidthProvider);
    final rounds = ref.watch(roundsProvider);
    return playerScores.when(
      skipLoadingOnReload: true,
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => Center(child: Text('$error')),
      data: (playerScores) {
        final selectedScore = playerScores.playerScores.firstWhereOrNull(
          (e) => e.id == selectedPlayerId,
        );
        return DataTable2(
          minWidth: double.infinity,
          fixedTopRows: selectedPlayerId != null ? 2 : 1,
          columns: [
            DataColumn2(
              label: const Text('#', maxLines: 1),
              numeric: true,
              fixedWidth: playerScores.maxRankWidth + columnMargin,
            ),
            DataColumn2(
              label: const Text('Player', maxLines: 1),
              fixedWidth: playerScores.maxNameWidth + columnMargin,
            ),
            DataColumn2(
              label: const Text('Total', maxLines: 1),
              numeric: true,
              fixedWidth: playerScores.maxScoreWidth + columnMargin,
            ),
            for (int i = rounds - 1; i >= 0; i--)
              DataColumn2(
                label: Text('R${i + 1}', maxLines: 1),
                numeric: true,
                fixedWidth: playerScores.maxScoreWidth + columnMargin,
              ),
            DataColumn2(
              label: const Text('Pen.', maxLines: 1),
              numeric: true,
              fixedWidth: playerScores.maxScoreWidth + columnMargin,
            ),
          ],
          rows: [
            if (selectedScore case PlayerScore score)
              ScoreRow(
                selected: true,
                score: score,
                rounds: rounds,
                onTap: () => onTap(context, selectedScore.id),
                color: WidgetStateProperty.all<Color>(selectedHighlight),
              ),
            for (final score in playerScores.playerScores)
              ScoreRow(
                selected: selectedPlayerId == score.id,
                score: score,
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
    required int rounds,
    required super.onTap,
    super.color,
    super.selected,
  }) : super(cells: [
          DataCell(Text(
            score.rank,
            maxLines: 1,
          )),
          DataCell(Text(
            score.name,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          )),
          DataCell(ScoreText(score.total)),
          for (int i = rounds - 1; i >= 0; i--)
            DataCell(
              ScoreText(score.roundScores.elementAtOrNull(i)?.score ?? 0),
            ),
          DataCell(ScoreText(score.penalty)),
        ]);
}
