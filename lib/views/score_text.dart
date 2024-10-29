import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' hide TextDirection;

import '/providers.dart';
import 'utils.dart';

const scoreStyle = TextStyle(
  fontWeight: FontWeight.bold,
  fontSize: 16,
);

Size scoreSize(int? score, String negSign) {
  if (score == null) return textSize('-', style: scoreStyle);
  return textSize(
    scoreFormat(score, negSign),
    style: scoreStyle,
  );
}

String scoreFormat(num score, String negSign) =>
    NumberFormat('+#0.0;$negSign#0.0').format(score / 10);

class ScoreText extends ConsumerWidget {
  const ScoreText(
    this.score, {
    TextStyle? style,
    super.key,
  }) : style = style ?? const TextStyle();

  final num? score;
  final TextStyle style;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (score == null) {
      return Text(
        '-',
        maxLines: 1,
        style: style.copyWith(
          fontWeight: FontWeight.bold,
          color: Theme.of(context).disabledColor,
        ),
      );
    }

    final negSign = ref.watch(negSignProvider);
    return Text(
      scoreFormat(score!, negSign),
      maxLines: 1,
      style: style.copyWith(
        fontWeight: FontWeight.bold,
        color: switch (score!) {
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

  final num? score;
  final TextStyle style;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (score == null) {
      return Text(
        '-',
        maxLines: 1,
        style: style.copyWith(
          color: Theme.of(context).disabledColor,
        ),
      );
    }

    final negSign = ref.watch(negSignProvider);
    return Text(
      scoreFormat(score!, negSign),
      maxLines: 1,
      style: style.copyWith(
        color: switch (score!) {
          > 0 => Colors.green,
          < 0 => Colors.red,
          _ => Theme.of(context).disabledColor,
        },
      ),
    );
  }
}
