import 'package:collection/collection.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import '/providers.dart';
import 'schedule_list.dart';
import 'score_text.dart';
import '/utils.dart';

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
    final gamesMap = ref.watch(gameProvider);
    List<Hanchan> games = [];
    if (gamesMap.hasValue) {
      games = gamesMap.value!.withPlayerId(playerId(context));
    }
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
            PlayerGameTab(player: player, games: games),
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

class PlayerGameTab extends ConsumerWidget {
  const PlayerGameTab({
    super.key,
    required this.player,
    required this.games,
  });

  final PlayerScore player;
  final List<Hanchan> games;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (games.isEmpty) {
      return const Center(
          child: Text('No game results available yet for this player'));
    }
    return ResultsTable(game: games[0],);
  }
}

class ResultsTable extends ConsumerWidget {
  const ResultsTable({
    super.key,
    required this.game,
  });

  final Hanchan game;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DataTable2(
      //minwidth: double.infinity,
      columns: const [
        DataColumn2(
          label: Text(""),
        ), // player
        DataColumn2(
          label: Text("game score"),
        ),
        DataColumn2(
          label: Text("place"),
        ),
        DataColumn2(
          label: Text("uma"),
        ),
        DataColumn2(
          label: Text("penalty"),
        ),
        DataColumn2(
          label: Text("final score"),
        ),
      ],
      rows: [
        for (final HanchanScore p in game.scores)
          DataRow2(cells: [
            DataCell(Text(p.playerId.toString())),
            DataCell(ScoreText(p.gameScore)),
            DataCell(Text(p.placement.toString())),
            DataCell(ScoreText(p.uma)),
            DataCell(ScoreText(p.penalties)),
            DataCell(ScoreText(p.finalScore)),
          ])
      ],
    );
  }
}
