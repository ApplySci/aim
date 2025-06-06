import 'package:collection/collection.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import '/providers.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import '/views/score_text.dart';
import '/views/viewutils.dart';

typedef PlayerRoundScore = ({
  int seat,
  String name,
  HanchanScore score,
});

final roundScoreListProvider =
    StreamProvider.autoDispose.family<List<PlayerRoundScore>, RoundId>(
  (ref, roundId) async* {
    final games = await ref.watch(gameProvider.future);
    final seatMap = await ref.watch(seatMapProvider.future);
    yield [
      for (final game in games)
        if (game.roundId == roundId)
          for (final table in game.tables)
            for (final score in table.scores)
              (
                seat: score.seat,
                name: seatMap[score.seat]!.name,
                score: score,
              ),
    ];
  },
);

typedef PlayerRoundScoreWidths = ({
  double maxNameWidth,
  double maxPlacementWidth,
  double maxGameScoreWidth,
  double maxFinalScoreWidth,
  double maxPenaltiesWith,
});

final roundScoreListWidthsProvider = StreamProvider.autoDispose
    .family<(PlayerRoundScoreWidths, List<PlayerRoundScore>, int?)?, RoundId>(
  (ref, roundId) async* {
    final negSign = ref.watch(negSignProvider);
    final roundScoreList = await ref.watch(roundScoreListProvider(roundId).future);
    final selectedSeat = ref.watch(selectedSeatProvider);

    if (roundScoreList.isEmpty) {
      yield (
        (
          maxNameWidth: 0,
          maxPlacementWidth: 0,
          maxGameScoreWidth: 0,
          maxFinalScoreWidth: 0,
          maxPenaltiesWith: 0,
        ),
        [],
        selectedSeat,
      );
    } else {
      yield (
        (
          maxNameWidth: roundScoreList.map((e) => textSize(e.name).width).max,
          maxPlacementWidth: roundScoreList
              .map((e) => textSize('${e.score.placement}').width)
              .max,
          maxGameScoreWidth: roundScoreList
              .map((e) => scoreSize(e.score.gameScore, negSign).width)
              .max,
          maxFinalScoreWidth: roundScoreList
              .map((e) => scoreSize(e.score.finalScore, negSign).width)
              .max,
          maxPenaltiesWith: roundScoreList
              .map((e) => scoreSize(e.score.penalties, negSign).width)
              .max,
        ),
        roundScoreList,
        selectedSeat,
      );
    }
  },
);

class RoundScoresTab extends ConsumerWidget {
  const RoundScoresTab({
    required this.round,
    super.key,
  });

  final RoundScheduleData round;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final roundScoreList = ref.watch(roundScoreListWidthsProvider(round.id));
    return roundScoreList.when(
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
      data: (data) {
        if (data == null) {
          return const Center(
            child: Text('No scores available yet'),
          );
        }
        final (widths, players, selectedSeat) = data;
        return DataTable2(
          minWidth: double.infinity,
          columnSpacing: 8,
          columns: [
            DataColumn2(
              label: const Text('Player'),
              fixedWidth: widths.maxNameWidth + 8,
            ),
            DataColumn2(
              label: const Text('#'),
              numeric: true,
              fixedWidth: widths.maxPlacementWidth + 8,
            ),
            DataColumn2(
              label: const Text('Game'),
              numeric: true,
              fixedWidth: widths.maxGameScoreWidth + 8,
            ),
            DataColumn2(
              label: const Text('Final'),
              numeric: true,
              fixedWidth: widths.maxFinalScoreWidth + 8,
            ),
            DataColumn2(
              label: const Text('Pen.'),
              numeric: true,
              fixedWidth: widths.maxPenaltiesWith + 8,
            ),
          ],
          rows: [
            for (final player in players)
              DataRow2(
                cells: [
                  DataCell(Text(player.name)),
                  DataCell(Text('${player.score.placement}')),
                  DataCell(ScoreText(player.score.gameScore)),
                  DataCell(ScoreText(player.score.finalScore)),
                  DataCell(PenaltyText(player.score.penalties)),
                ],
                selected: selectedSeat == player.seat,
                color: selectedSeat == player.seat
                    ? WidgetStateColor.resolveWith((states) =>
                        Theme.of(context).colorScheme.primaryContainer)
                    : null,
              )
          ],
        );
      },
    );
  }
}
