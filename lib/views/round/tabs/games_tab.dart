import 'package:collection/collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_sticky_header/flutter_sticky_header.dart';

import '/models.dart';
import '/providers.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import '/views/score_text.dart';
import '/views/table_score_table.dart';
import '/views/utils.dart';

typedef RoundTableScores = ({
  Hanchan table,
  List<TablePlayerScore> players,
});

final roundScoresProvider =
    StreamProvider.autoDispose.family<List<RoundTableScores>, RoundId>(
  (ref, roundId) async* {
    final games = await ref.watch(gameProvider.future);
    final seatMap = await ref.watch(seatMapProvider.future);
    yield [
      for (final game in games)
        if (game.roundId == roundId)
          for (final table in game.tables)
            (
              table: table,
              players: [
                for (final score in table.scores)
                  (
                    player: seatMap[score.seat]!,
                    score: score,
                  ),
              ],
            ),
    ]..sort((a, b) => int.parse(a.table.tableId.replaceAll(RegExp(r'[^\d]'), ''))
        .compareTo(int.parse(b.table.tableId.replaceAll(RegExp(r'[^\d]'), ''))));
  },
);

final roundGamesWithWidthsProvider = StreamProvider.autoDispose
    .family<(TableScoreWidths, List<RoundTableScores>)?, RoundId>(
  (ref, roundId) async* {
    final negSign = ref.watch(negSignProvider);
    final scores = await ref.watch(roundScoresProvider(roundId).future);
    if (scores.isEmpty) {
      yield null;
      return;
    }

    final gameSize = textSize('Game').width;
    final penaltySize = textSize('Pen.').width;
    final finalSize = textSize('Final').width;
    final maxScoreWidth = scores
        .map((a) => a.players)
        .flattened
        .map((score) => scoreSize(score.score.gameScore, negSign).width);
    final maxPenaltyWidth = scores
        .map((a) => a.players)
        .flattened
        .map((score) => scoreSize(score.score.penalties, negSign).width);
    final maxFinalScoreWidth = scores
        .map((a) => a.players)
        .flattened
        .map((score) => scoreSize(score.score.finalScore, negSign).width);

    yield (
      (
        maxNameWidth: scores
            .map((a) => a.players)
            .flattened
            .map((score) => textSize(score.player.name).width)
            .max,
        maxScoreWidth: [
          gameSize,
          penaltySize,
          finalSize,
        ]
            .followedBy(maxScoreWidth)
            .followedBy(maxPenaltyWidth)
            .followedBy(maxFinalScoreWidth)
            .max,
        maxPlaceWidth: scores
            .map((a) => a.players)
            .flattened
            .map((score) => textSize('${score.score.placement}').width)
            .max,
        maxUmaWidth: scores
            .map((a) => a.players)
            .flattened
            .map((score) => scoreSize(score.score.uma, negSign).width)
            .max,
      ),
      scores,
    );
  },
);

class RoundGamesTab extends ConsumerWidget {
  const RoundGamesTab({
    required this.round,
    super.key,
  });

  final RoundScheduleData round;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final games = ref.watch(roundGamesWithWidthsProvider(round.id));
    return games.when(
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
      data: (data) {
        if (data == null) {
          return const Center(
            child: Text('No game results available yet'),
          );
        }
        final (widths, tables) = data;
        return CustomScrollView(
          slivers: [
            for (final table in tables)
              SliverStickyHeader(
                header: Material(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  elevation: 1,
                  child: ListTile(
                    title: Text(table.table.tableId),
                    visualDensity: VisualDensity.compact,
                  ),
                ),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    TableScoreTable(
                      widths: widths,
                      players: table.players,
                    ),
                  ]),
                ),
              ),
          ],
        );
      },
    );
  }
}
