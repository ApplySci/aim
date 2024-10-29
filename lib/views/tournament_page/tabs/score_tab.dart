import 'package:collection/collection.dart';
import 'package:flutter/material.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/utils.dart';
import '/views/data_table_2d.dart';
import '/views/datatable2_fixed_line.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import '/views/rank_text.dart';
import '/views/score_text.dart';
import '/views/utils.dart';

const columnMargin = 18;

final scoreWidthProvider = StreamProvider.autoDispose((ref) async* {
  final negSign = ref.watch(negSignProvider);
  final playerScores = await ref.watch(playerScoreListProvider.future);
  final maxScoreWidth = playerScores
      .map((playerScore) => playerScore.scores)
      .flattened
      .where((score) => score != null)  // Filter out null scores
      .map((score) => scoreSize(score!.finalScore, negSign).width);
  final maxTotalWidth = playerScores
      .map((playerScore) => playerScore.total)
      .map((score) => scoreSize(score, negSign).width);
  final maxPenaltyWidth = playerScores
      .map((playerScore) => playerScore.penalty)
      .map((score) => scoreSize(score, negSign).width);

  double? maxRank, maxName, maxScore;
  try {
    maxRank = playerScores.map((e) => rankSize(e.rank, e.tied).width).max;
    maxName = playerScores.map((e) => textSize(e.name).width).max;
    maxScore = maxScoreWidth.followedBy(maxTotalWidth).followedBy(maxPenaltyWidth).max;
  } catch(e) {
    maxRank ??= 1;
    maxName ??= 1;
    maxScore ??= 1;
  }

  yield (
    playerScores: playerScores,
    maxRankWidth: maxRank,
    maxNameWidth: maxName,
    maxScoreWidth: maxScore,
  );
});

class ScoreTable extends ConsumerWidget {
  const ScoreTable({super.key});

  void onTap(BuildContext context, int seat) =>
      Navigator.of(context).pushNamed(ROUTES.player, arguments: {'seat': seat});

  @override
  Widget build(context, ref) {
    final selectedSeat = ref.watch(selectedSeatProvider);
    AsyncValue<({
        double maxNameWidth,
        double maxRankWidth,
        double maxScoreWidth,
        List<PlayerScore> playerScores
      })> playerScores;
    try {
      playerScores = ref.watch(scoreWidthProvider);
    }
    catch (e) {
      return const LoadingView();
    }
    return playerScores.when(
      skipLoadingOnReload: true,
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
      data: (playerScores) {
        int? indexSelected;
        if (selectedSeat != null) {
          indexSelected = playerScores.playerScores.indexWhere(
                (e) => e.seat == selectedSeat,
          );
        }
        final int rounds = playerScores.playerScores.isEmpty
            ? 0
            : playerScores.playerScores[0].scores.length;
        if (rounds==0) {
          return const Center(child: Text('No scores available yet'),);
        }
        return DataTable2FixedLine(
          key: ValueKey(selectedSeat),
          minWidth: double.infinity,
          fixedRow: indexSelected,
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
            // TODO what if a player doesn't have a score for a particular round?
            for (final score in playerScores.playerScores)
              ScoreRow(
                selected: selectedSeat == score.seat,
                score: score,
                rounds: rounds,
                onTap: () => onTap(context, score.seat),
                decoration: selectedSeat == score.seat
                    ? BoxDecoration(
                      border: Border.all(
                        color: Colors.green, // Border color
                        width: 2.0,         // Border width
                      ))
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
    required super.onTap,
    required int rounds,
    super.color,
    super.selected,
    super.decoration,
  }) : super(cells: [
          DataCell(RankText(
            rank: score.rank,
            tied: score.tied,
          )),
          DataCell(Text(
            score.name,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          )),
          DataCell(ScoreText(score.total)),
          for (int i = rounds - 1; i >= 0; i--)
            DataCell(
              i < score.scores.length 
                  ? (score.scores[i]?.finalScore != null 
                      ? ScoreText(score.scores[i]!.finalScore)
                      : const Text('-'))
                  : const Text('-'),
            ),
          DataCell(PenaltyText(score.penalty)),
        ]);
}
