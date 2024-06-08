import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' hide TextDirection;

import '/providers.dart';

const scoreStyle = TextStyle(
  fontWeight: FontWeight.bold,
  fontSize: 16,
);

Size textSize(String text, {TextStyle? style}) {
  return (TextPainter(
    text: TextSpan(text: text, style: style),
    maxLines: 1,
    textDirection: TextDirection.ltr,
  )..layout())
      .size;
}

Size scoreSize(int score, String negSign) => textSize(
      // Display score with 1 decimal point
      scoreFormat(score, negSign),
      style: scoreStyle,
    );

String scoreFormat(num score, String negSign) =>
    NumberFormat('+#0.0;$negSign#0.0').format(score / 10);

class ScoreText extends ConsumerWidget {
  const ScoreText(
    this.score, {
    TextStyle? style,
    super.key,
  }) : style = style ?? const TextStyle();

  final num score;
  final TextStyle style;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final negSign = ref.watch(negSignProvider);
    return Text(
      scoreFormat(score, negSign),
      maxLines: 1,
      style: style.copyWith(
        fontWeight: FontWeight.bold,
        color: switch (score) {
          > 0 => Colors.green,
          < 0 => Colors.red,
          _ => null,
        },
      ),
    );
  }
}

class PenaltyText extends ConsumerWidget {
  const PenaltyText(
    this.score, {
    TextStyle? style,
    super.key,
  }) : style = style ?? const TextStyle();

  final num score;
  final TextStyle style;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final negSign = ref.watch(negSignProvider);
    return Text(
      scoreFormat(score, negSign),
      maxLines: 1,
      style: style.copyWith(
        color: switch (score) {
          > 0 => Colors.green,
          < 0 => Colors.red,
          _ => Theme.of(context).disabledColor,
        },
      ),
    );
  }
}
