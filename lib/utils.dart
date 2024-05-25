/*

 Utility functions, enums and constants used across the app

 This should NEVER import things from elsewhere in the app.
 This is to avoid circular dependencies.

 */
import 'dart:async';

import 'package:alarm/alarm.dart';
import 'package:alarm/model/alarm_settings.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

enum LOG {
  debug,
  info,
  score,
  unusual,
  warn,
  error,
}

const enableAlarm = kReleaseMode || false;

const String defaultColourKey = 'black knight';

const Map<String, Color> backgroundColours = {
  defaultColourKey: Colors.black,
  'fireball red': Color(0xFF330000),
  'deep purple': Color(0xFF220033),
};

String dateRange(Timestamp? startDT, Timestamp? endDT) {
  if (startDT == null || endDT == null) return '';
  final sd = startDT.toDate();
  final ed = endDT.toDate();
  String start = 'ERROR: unassigned dateRange!';
  if (sd.year == ed.year) {
    if (sd.month == ed.month && sd.day == ed.day) {
      start = DateFormat('HH:mm').format(sd);
    } else {
      start = DateFormat('HH:mm d MMM').format(sd);
    }
  } else {
    start = DateFormat('HH:mm d MMM y').format(sd);
  }
  final end = DateFormat('HH:mm d MMM y').format(ed);
  return '$start - $end';
}

class ROUTES {
  static const String home = '/home';
  static const String privacyPolicy = '/privacyPolicy';
  static const String settings = '/settings';
  static const String tournaments = '/tournaments';
  static const String tournament = '/tournament';
  static const String player = '/player';
}

const Color selectedHighlight = Color(0x88aaaaff);

class Log {
  static List<List<dynamic>> logs = [];

  static void debug(String text) {
    debugPrint(text);
  }

  static void _saveLog(LOG type, String text) {
    final typeString = type.name;
    logs.add([DateTime.now().toIso8601String(), typeString, text]);
    debug('$typeString : $text');
  }

  static void unusual(String text) {
    _saveLog(LOG.unusual, text);
  }

  static void warn(String text) {
    _saveLog(LOG.warn, text);
  }

  static void error(String text) {
    _saveLog(LOG.error, text);
  }

  static void info(String text) {
    _saveLog(LOG.info, text);
  }
}

typedef RunOrQueueValue = ({
  Future<void> future,
  FutureOr<void> Function() current,
  FutureOr<void> Function()? next,
});

class RunOrQueue {
  RunOrQueue._();

  RunOrQueueValue? _queue;

  Future<void> call(FutureOr<void> Function() block) async {
    if (_queue case RunOrQueueValue queue) {
      _queue = (
        future: queue.future,
        current: queue.current,
        next: block,
      );
      return await queue.future;
    }

    final completer = Completer<void>();
    _queue = (
      future: completer.future,
      current: block,
      next: null,
    );
    while (_queue != null) {
      try {
        await _queue!.current();
      } finally {
        _queue = switch (_queue) {
          (
            future: Future<void> future,
            current: FutureOr<void> Function() _,
            next: FutureOr<void> Function() current,
          ) =>
            (
              future: future,
              current: current,
              next: null,
            ),
          _ => null,
        };
      }
    }
    completer.complete();
  }
}

final alarmRunner = RunOrQueue._();

// Function to store alarm ID
Future<void> setAlarm(
  DateTime when,
  String title,
  String body,
  int id,
) async {
  final alarmSettings = AlarmSettings(
    id: id,
    dateTime: when,
    assetAudioPath: 'assets/audio/notif.mp3',
    loopAudio: false,
    vibrate: true,
    volume: null,
    fadeDuration: 0,
    notificationTitle: title,
    notificationBody: body,
  );
  await Alarm.set(alarmSettings: alarmSettings);
}

extension SeperatedBy<T> on Iterable<T> {
  Iterable<T> seperatedBy(T seperator) sync* {
    if (isEmpty) return;

    final iterator = this.iterator;
    iterator.moveNext();
    yield iterator.current;
    while (iterator.moveNext()) {
      yield seperator;
      yield iterator.current;
    }
  }
}
