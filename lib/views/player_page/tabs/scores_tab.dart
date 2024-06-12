import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/views/score_text.dart';

class PlayerScoreTab extends ConsumerWidget {
  const PlayerScoreTab({
    required this.player,
    super.key,
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
