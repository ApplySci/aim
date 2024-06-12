import 'package:collection/collection.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_sticky_header/flutter_sticky_header.dart';
import 'package:intl/intl.dart';

import '/models.dart';
import '/providers.dart';
import '/utils.dart';
import 'schedule_list.dart';
import 'score_text.dart';
import 'table_score_table.dart';
import 'utils.dart';

final playerScoreProvider = StreamProvider.family
    .autoDispose<PlayerScore, PlayerId>((ref, playerId) async* {
  final playerScoreList = await ref.watch(playerScoreListProvider.future);
  yield playerScoreList.firstWhere((e) => e.id == playerId);
});

class PlayerPage extends ConsumerWidget {
  const PlayerPage({
    super.key,
  });

  PlayerId playerId(BuildContext context) {
    return ModalRoute.of(context)?.settings.arguments as PlayerId;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final player = ref.watch(playerScoreProvider(playerId(context)));
    final isSelected = ref.watch(
      selectedPlayerIdProvider.select((id) => id == playerId(context)),
    );
    return player.when(
      skipLoadingOnReload: true,
      loading: () => Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: const Text('Player'),
        ),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (error, stackTrace) => Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: const Text('Player'),
        ),
        body: ErrorScreen(error: error, stackTrace: stackTrace),
      ),
      data: (player) => DefaultTabController(
        length: 4,
        child: Scaffold(
          appBar: AppBar(
            backgroundColor: Theme.of(context).colorScheme.inversePrimary,
            title: Text(player.name),
            actions: [
              IconButton(
                onPressed: () {
                  final selectedPlayerIdNotifier =
                      ref.read(selectedPlayerIdProvider.notifier);
                  if (isSelected) {
                    selectedPlayerIdNotifier.set(null);
                  } else {
                    selectedPlayerIdNotifier.set(player.id);
                  }
                },
                icon: isSelected
                    ? const Icon(Icons.favorite)
                    : const Icon(Icons.favorite_border),
              ),
            ],
            bottom: const TabBar(tabs: [
              Tab(text: 'Stats'),
              Tab(text: 'Schedule'),
              Tab(text: 'Scores'),
              Tab(text: 'Games'),
            ]),
          ),
          body: TabBarView(children: [
            PlayerStatsTab(player: player),
            PlayerScheduleTab(player: player),
            PlayerScoreTab(player: player),
            PlayerGameTab(player: player),
          ]),
        ),
      ),
    );
  }
}

class PlayerStatsTab extends ConsumerWidget {
  const PlayerStatsTab({
    super.key,
    required this.player,
  });

  final PlayerScore player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(children: [
      ListTile(
        title: const Text('Current Overall Score'),
        trailing: ScoreText(
          player.total,
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
      ListTile(
        title: const Text('Penalty'),
        trailing: ScoreText(
          player.penalty,
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
      ListTile(
        title: const Text('Average Score'),
        trailing: ScoreText(
          player.scores.map((e) => e.finalScore).average,
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
      ListTile(
        title: const Text('Highest Score'),
        trailing: ScoreText(
          player.scores.map((e) => e.finalScore).max,
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
      ListTile(
        title: const Text('Lowest Score'),
        trailing: ScoreText(
          player.scores.map((e) => e.finalScore).min,
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
    ]);
  }
}

class PlayerScheduleTab extends ConsumerWidget {
  const PlayerScheduleTab({
    super.key,
    required this.player,
  });

  final PlayerScore player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ProviderScope(
      overrides: [
        showAllProvider.overrideWith((ref) => false),
        filterByPlayerIdProvider.overrideWith((ref) => player.id),
      ],
      child: const ScheduleList(when: When.all),
    );
  }
}

class PlayerScoreTab extends ConsumerWidget {
  const PlayerScoreTab({
    super.key,
    required this.player,
  });

  final PlayerScore player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (player.scores.isEmpty) {
      return const Center(child: Text('No Rounds Played'));
    }

    return DataTable2(
      columns: const [
        DataColumn2(label: Text('Round')),
        DataColumn2(
          label: Text('Score'),
          fixedWidth: 80,
          numeric: true,
        ),
      ],
      rows: [
        for (final (index, score) in player.scores.indexed)
          DataRow2(cells: [
            DataCell(Text('Round ${index + 1}')),
            DataCell(ScoreText(score.finalScore)),
          ]),
      ],
    );
  }
}

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
    super.key,
    required this.player,
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
