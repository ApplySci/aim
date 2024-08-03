import 'package:collection/collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/views/score_text.dart';

class PlayerStatsTab extends ConsumerWidget {
  const PlayerStatsTab({
    required this.player,
    super.key,
  });

  final PlayerScore player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (player.scores.isEmpty) {
      return const Center(
        child: Text('No scores available yet'),
      );
    }
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
