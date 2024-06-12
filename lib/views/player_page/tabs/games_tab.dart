import 'package:collection/collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_sticky_header/flutter_sticky_header.dart';
import 'package:intl/intl.dart';

import '/models.dart';
import '/providers.dart';
import '/utils.dart';
import '/views/score_text.dart';
import '/views/table_score_table.dart';
import '/views/utils.dart';

typedef PlayerRounds = ({
  RoundScheduleData round,
  List<TablePlayerScore> players,
});

final playerScoresProvider =
    StreamProvider.autoDispose.family<List<PlayerRounds>, PlayerId>(
  (ref, playerId) async* {
    final games = (await ref.watch(gameProvider.future)).withPlayerId(playerId);
    final roundMap = await ref.watch(roundMapProvider.future);
    final playerMap = await ref.watch(playerMapProvider.future);
    yield [
      for (final game in games)
        (
          round: roundMap[game.roundId]!,
          players: [
            for (final score in game.scores)
              (
                player: playerMap[score.playerId]!,
                score: score,
              )
          ]
        ),
    ];
  },
);

final playerGamesWithWidthsProvider = StreamProvider.autoDispose
    .family<(TableScoreWidths, List<PlayerRounds>)?, PlayerId>(
  (ref, playerId) async* {
    final negSign = ref.watch(negSignProvider);
    final scores = await ref.watch(playerScoresProvider(playerId).future);
    if (scores.isEmpty) {
      yield null;
      return;
    }

    final gameSize = textSize('Game').width;
    final penaltySize = textSize('Pen.').width;
    final finalSize = textSize('Final').width;
    final maxScoreWidth = scores
        .map((e) => e.players)
        .flattened
        .map((score) => scoreSize(score.score.gameScore, negSign).width);
    final maxPenaltyWidth = scores
        .map((e) => e.players)
        .flattened
        .map((score) => scoreSize(score.score.penalties, negSign).width);
    final maxFinalScoreWidth = scores
        .map((e) => e.players)
        .flattened
        .map((score) => scoreSize(score.score.finalScore, negSign).width);

    yield (
      (
        maxNameWidth: scores
            .map((e) => e.players)
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
            .map((e) => e.players)
            .flattened
            .map((score) => textSize('${score.score.placement}').width)
            .max,
        maxUmaWidth: scores
            .map((e) => e.players)
            .flattened
            .map((score) => scoreSize(score.score.uma, negSign).width)
            .max,
      ),
      scores,
    );
  },
);

class PlayerGameTab extends ConsumerWidget {
  const PlayerGameTab({
    required this.player,
    super.key,
  });

  final PlayerScore player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final games = ref.watch(playerGamesWithWidthsProvider(player.id));
    return games.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) =>
          ErrorScreen(error: error, stackTrace: stackTrace),
      data: (data) {
        if (data == null) {
          return const Center(
            child: Text('No game results available yet for this player'),
          );
        }
        final (widths, rounds) = data;
        return CustomScrollView(
          slivers: [
            for (final round in rounds)
              SliverStickyHeader(
                header: Material(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  elevation: 1,
                  child: ListTile(
                    leading: const Icon(Icons.watch_later_outlined),
                    title: Text(round.round.name),
                    subtitle: Text(
                      DateFormat('EEEE d MMMM HH:mm').format(round.round.start),
                    ),
                    visualDensity: VisualDensity.compact,
                    onTap: () => Navigator.of(context).pushNamed(
                      ROUTES.round,
                      arguments: round.round.id,
                    ),
                  ),
                ),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    TableScoreTable(
                      widths: widths,
                      players: round.players,
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
