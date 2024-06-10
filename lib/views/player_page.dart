import 'package:collection/collection.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '/models.dart';
import '/providers.dart';
import '/utils.dart';
import 'schedule_list.dart';
import 'score_text.dart';
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
        // uses ErrorScreen
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
    final scores = player.roundScores.map((e) => e.score);
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
          scores.average,
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
      ListTile(
        title: const Text('Highest Score'),
        trailing: ScoreText(
          scores.max,
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
      ListTile(
        title: const Text('Lowest Score'),
        trailing: ScoreText(
          scores.min,
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
    if (player.roundScores.isEmpty) {
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
        for (final (index, score) in player.roundScores.indexed)
          DataRow2(cells: [
            DataCell(Text('Round ${index + 1}')),
            DataCell(ScoreText(score.score)),
          ]),
      ],
    );
  }
}

typedef PlayerHanchanScore = ({
  PlayerData player,
  HanchanScore score,
});

typedef RoundHanchanScore = ({
  RoundScheduleData round,
  List<PlayerHanchanScore> players,
});

typedef PlayerGamesWithWidths = ({
  List<RoundHanchanScore> rounds,
  double maxNameWidth,
  double maxScoreWidth,
  double maxPlaceWidth,
  double maxUmaWidth,
});

final playerScoresProvider =
    StreamProvider.autoDispose.family<List<RoundHanchanScore>, PlayerId>(
  (ref, playerId) async* {
    final games = (await ref.watch(gameProvider.future)).withPlayerId(playerId);
    final roundMap = await ref.watch(scheduleProvider.selectAsync((schedule) {
      return {
        for (final round in schedule.rounds) round.id: round,
      };
    }));
    final playerMap = await ref.watch(playerListProvider.selectAsync((players) {
      return {
        for (final player in players) player.id: player,
      };
    }));
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
          ],
        )
    ];
  },
);

final playerGamesWithWidthsProvider =
    StreamProvider.autoDispose.family<PlayerGamesWithWidths?, PlayerId>(
  (ref, playerId) async* {
    final negSign = ref.watch(negSignProvider);
    final playerScores = await ref.watch(playerScoresProvider(playerId).future);
    if (playerScores.isEmpty) {
      yield null;
      return;
    }

    final gameSize = textSize('Game').width;
    final penaltySize = textSize('Pen.').width;
    final finalSize = textSize('Final').width;
    final maxScoreWidth = playerScores
        .map((a) => a.players)
        .flattened
        .map((score) => scoreSize(score.score.gameScore, negSign).width);
    final maxPenaltyWidth = playerScores
        .map((a) => a.players)
        .flattened
        .map((score) => scoreSize(score.score.penalties, negSign).width);
    final maxFinalScoreWidth = playerScores
        .map((a) => a.players)
        .flattened
        .map((score) => scoreSize(score.score.finalScore, negSign).width);

    yield (
      rounds: playerScores,
      maxNameWidth: playerScores
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
      maxPlaceWidth: playerScores
          .map((a) => a.players)
          .flattened
          .map((score) => textSize('${score.score.placement}').width)
          .max,
      maxUmaWidth: playerScores
          .map((a) => a.players)
          .flattened
          .map((score) => scoreSize(score.score.uma, negSign).width)
          .max,
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
      data: (games) {
        if (games == null) {
          return const Center(
            child: Text('No game results available yet for this player'),
          );
        }
        return ListView(
          children: [
            for (final round in games.rounds)
              SizedBox(
                height: 312,
                child: Column(
                  children: [
                    Material(
                      color: Theme.of(context).colorScheme.primaryContainer,
                      elevation: 1,
                      child: ListTile(
                        leading: const Icon(Icons.watch_later_outlined),
                        title: Text(round.round.name),
                        subtitle: Text(
                          DateFormat('EEEE d MMMM HH:mm')
                              .format(round.round.start),
                        ),
                        visualDensity: VisualDensity.compact,
                      ),
                    ),
                    Expanded(
                      child: ResultsTable(
                        widths: games,
                        round: round,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        );
      },
    );
  }
}

class ResultsTable extends ConsumerWidget {
  const ResultsTable({
    super.key,
    required this.widths,
    required this.round,
  });

  final PlayerGamesWithWidths widths;
  final RoundHanchanScore round;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DataTable2(
      columnSpacing: 8,
      columns: [
        const DataColumn2(
          label: Text("Player"),
        ), // player
        DataColumn2(
          label: const Text("#"),
          numeric: true,
          fixedWidth: widths.maxPlaceWidth + 8,
        ),
        DataColumn2(
          label: const Text("Game"),
          numeric: true,
          fixedWidth: widths.maxScoreWidth + 8,
        ),
        DataColumn2(
          label: const Text("Uma"),
          numeric: true,
          fixedWidth: widths.maxUmaWidth + 8,
        ),
        DataColumn2(
          label: const Text("Pen."),
          numeric: true,
          fixedWidth: widths.maxScoreWidth + 8,
        ),
        DataColumn2(
          label: const Text("Final"),
          numeric: true,
          fixedWidth: widths.maxScoreWidth + 8,
        ),
      ],
      rows: [
        for (final player in round.players)
          DataRow2(cells: [
            DataCell(Text(player.player.name)),
            DataCell(Text(player.score.placement.toString())),
            DataCell(ScoreText(player.score.gameScore)),
            DataCell(ScoreText(player.score.uma)),
            DataCell(PenaltyText(player.score.penalties)),
            DataCell(ScoreText(player.score.finalScore)),
          ])
      ],
    );
  }
}
