import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class ScoreCell extends DataCell {
  final int score;
  final String negSign;
  ScoreCell(this.score, this.negSign, GestureTapCallback? onTap)
      : super(InkWell(
          onTap: onTap,
          child: Text(
            NumberFormat('+#0.0;$negSign#0.0'
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
