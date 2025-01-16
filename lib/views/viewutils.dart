import 'package:flutter/material.dart';
import 'package:timezone/timezone.dart' as tz;

Size textSize(String text, {TextStyle? style}) {
  return (TextPainter(
    text: TextSpan(text: text, style: style),
    maxLines: 1,
    textDirection: TextDirection.ltr,
  )..layout())
      .size;
}

String formatTimeWithDifference(tz.TZDateTime eventTime, tz.Location localTimeZone) {
  final localTime = tz.TZDateTime.from(eventTime, localTimeZone);
  final difference = eventTime.timeZoneOffset - localTime.timeZoneOffset;

  final hours = difference.inHours;
  final minutes = difference.inMinutes.remainder(60);

  String differenceString;
  if (hours == 0 && minutes == 0) {
    differenceString = '';
  } else {
    final parts = <String>[];
    if (hours != 0) {
      parts.add('${hours.abs()}h');
    }
    if (minutes != 0) {
      parts.add('${minutes.abs()}m');
    }
    differenceString = '(${difference.isNegative ? '-' : '+'}${parts.join(' ')})';
  }

  return '${eventTime.hour.toString().padLeft(2, '0')}:${eventTime.minute.toString().padLeft(2, '0')} $differenceString';
}
