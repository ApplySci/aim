import 'package:flutter/material.dart';

Size textSize(String text, {TextStyle? style}) {
  return (TextPainter(
    text: TextSpan(text: text, style: style),
    maxLines: 1,
    textDirection: TextDirection.ltr,
  )..layout())
      .size;
}
