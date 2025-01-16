import 'package:data_table_2/data_table_2.dart';
import 'package:flutter/material.dart';

import '/models.dart';
import 'score_text.dart';

typedef TablePlayerScore = ({
  PlayerData player,
  HanchanScore score,
});

typedef TableScoreWidths = ({
  double maxNameWidth,
  double maxScoreWidth,
  double maxPlaceWidth,
  double maxUmaWidth,
});

class TableScoreTable extends StatelessWidget {
  const TableScoreTable({
    required this.widths,
    required this.players,
    this.selectedSeat,
    super.key,
  });

  final TableScoreWidths widths;
  final List<TablePlayerScore> players;
  final int? selectedSeat;

  @override
  Widget build(BuildContext context) {
    final highlightColor = Theme.of(context).colorScheme.primaryContainer;
    
    return SizedBox(
      height: 248,
      child: DataTable2(
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
          for (final player in players)
            DataRow2(
              selected: selectedSeat == player.player.seat,
              color: selectedSeat == player.player.seat
                  ? WidgetStateColor.resolveWith((states) => highlightColor)
                  : null,
              cells: [
                DataCell(Text(player.player.name)),
                DataCell(Text(player.score.placement.toString())),
                DataCell(ScoreText(player.score.gameScore)),
                DataCell(ScoreText(player.score.uma)),
                DataCell(PenaltyText(player.score.penalties)),
                DataCell(ScoreText(player.score.finalScore)),
              ],
            )
        ],
      ),
    );
  }
}
