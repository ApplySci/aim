import 'package:flutter/material.dart';

class ScoreCell extends DataCell {
  final int score;
  final onTap;

  ScoreCell(this.score, this.onTap)
      : super(
          InkWell(
            onTap: onTap,
            onDoubleTap: onTap,
            onLongPress: onTap,
            child: Container(
              color: Colors.black,
              child: Center(
                child: Text(
                  (score / 10).toStringAsFixed(1),
                  // Display score with 1 decimal point
                  style: TextStyle(
                    color: score > 0 ? Colors.green :
                    (score < 0 ? Colors.red : Colors.white),
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ),
            ),
          ),
        );
}
