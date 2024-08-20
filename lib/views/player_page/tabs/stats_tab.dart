import 'package:collection/collection.dart';
import 'package:flutter/material.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import '/providers.dart';
import '/views/score_text.dart';
import '/views/my_spark_chart.dart';


class PlayerStatsTab extends ConsumerWidget {
  const PlayerStatsTab({
    required this.player,
    super.key,
  });

  final PlayerRankings player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (player.games.scores.isEmpty) {
      return const Center(
        child: Text('No scores available yet'),
      );
    }

    List<int> scores = [for (HanchanScore s in player.games.scores)
      s.finalScore];
    List<int> rankings = player.rankings;
    List<int> totals = player.totalScores;

    return ListView(
      children: [
        ListTile(
          title: const Text('Current Overall Score'),
          trailing: ScoreText(
            player.games.total,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        ListTile(
          title: const Text('Out-of-game penalties'),
          trailing: ScoreText(
            player.games.penalty,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        ListTile(
          title: const Text('In-game penalties'),
          trailing: ScoreText(
            player.games.scores.map((e) => e.penalties).sum,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        ListTile(
          title: const Text('Average Score'),
          trailing: ScoreText(
            player.games.scores.map((e) => e.finalScore).average,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        ListTile(
          title: const Text('Highest Score'),
          trailing: ScoreText(
            player.games.scores.map((e) => e.finalScore).max,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        ListTile(
          title: const Text('Lowest Score'),
          trailing: ScoreText(
            player.games.scores.map((e) => e.finalScore).min,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        const ListTile(
          title: Text('Ranking'),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: SizedBox(
            height: 150,
            child: MySparkChart(
              data: [for (int r in rankings) -1.0 * r],
              labelTextCallback: (y) => Text('${y.abs().toInt()}'),
            ),
          ),
        ),
        const ListTile(
          title: Text('Total score'),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: SizedBox(
            height: 200,
            child: MySparkChart(
              axisLineColor: Colors.green,
              data: totals,
              labelTextCallback: (y) => ScoreText(y),
            ),
          ),
        ),
        const ListTile(
          title: Text('Game scores'),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: SizedBox(
            height: 200,
            child: MySparkChart(
              chartType: MySparkChartType.bar,
              data: scores.reversed.toList(),
              labelTextCallback: (y) => ScoreText(y),
            ),
          ),
        ),
      ],
    );
  }
}
