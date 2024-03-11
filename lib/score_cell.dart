import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'store.dart';

class ScoreCell extends DataCell {
  final int score;
  @override
  final onTap;

  ScoreCell(this.score, this.onTap)
      : super(InkWell(
          onTap: onTap,
          child: Text(
            NumberFormat('+#0.0;${store.state.preferences['japaneseNumbers'] ? '▲' : '-'}#0.0'
            ).format(score / 10),
            // Display score with 1 decimal point
            style: TextStyle(
              color: Color(
                score > 0 ? 0xff00bb00 : (score < 0 ? 0xff660000 : 0xffbbbbbb)
              ),
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ),
  );
}
