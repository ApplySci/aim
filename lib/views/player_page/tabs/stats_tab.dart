import 'package:collection/collection.dart';
import 'package:flutter/material.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

import '/providers.dart';
import '/views/score_text.dart';
import '/views/my_spark_chart.dart';


class PlayerStatsTab extends ConsumerWidget {
  const PlayerStatsTab({
    required this.player,
    super.key,
  });

  final PlayerScore player;

  renderLabel(DataLabelRenderArgs args) {

  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (player.scores.isEmpty) {
      return const Center(
        child: Text('No scores available yet'),
      );
    }

    // TODO prepare List<int> of ranks, and List<double> of scores
    List<double> scores = [-20.5, 40.2, 60.0, 120.8, 75.4, 20.1, -30.4];
    List<int> rankings = [1,20,29,30,15,40,45];
    List<double> totals = [-20.5, 40.2, 60.0, 120.8, 75.4, 20.1, -30.4];

    return ListView(
      children: [
        ListTile(
          title: const Text('Current Overall Score'),
          trailing: ScoreText(
            player.total,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        ListTile(
          title: const Text('Out-of-game penalties'),
          trailing: ScoreText(
            player.penalty,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        ListTile(
          title: const Text('In-game penalties'),
          trailing: ScoreText(
            player.scores.map((e) => e.penalties).sum,
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
        const ListTile(
          title: Text('Ranking'),
        ),
        // hardcoded chart as proof of principle
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
        // hardcoded chart as proof of principle
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: SizedBox(
            height: 200,
            child: MySparkChart(
              axisLineColor: Colors.green,
              data: totals,
              labelTextCallback: (y) => Text('${y>0 ? "+" : ""}$y'),
            ),
          ),
        ),
        const ListTile(
          title: Text('Game scores'),
        ),
        // hardcoded chart as proof of principle
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: SizedBox(
            height: 200,
            child: MySparkChart(
              chartType: MySparkChartType.bar,
              data: scores,
              labelTextCallback: (y) => Text('${y>0 ? "+" : ""}$y'),
            ),
          ),
        ),
      ],
    );
  }
}
