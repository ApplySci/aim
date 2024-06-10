import 'package:flutter/material.dart';

import 'utils.dart';

String rankText(int rank, bool tied) => '${tied ? '=' : ''}$rank';

Size rankSize(int rank, bool tied) => textSize(rankText(rank, tied));

class RankText extends StatelessWidget {
  const RankText({
    required this.rank,
    required this.tied,
    TextStyle? style,
    super.key,
  }) : style = style ?? const TextStyle();

  final int rank;
  final bool tied;
  final TextStyle style;

  @override
  Widget build(BuildContext context) => Text(
        rankText(rank, tied),
        style: style,
      );
}
