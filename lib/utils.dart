/*

 Utility functions, enums and constants used across the app

 This should NEVER import things from elsewhere in the app.
 This is to avoid circular dependencies.

 */
import 'dart:async';

import 'package:equatable/equatable.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

FirebaseMessaging messaging = FirebaseMessaging.instance;

void unassigned() {}

String enumToString<T>(T o) {
  return o.toString().split('.').last;
}

T enumFromString<T>(String key, List<T> values) {
  return values.firstWhere((v) => key == enumToString(v));
}

enum LOG { debug, info, score, unusual, warn, error }

enum STORE {
  setPlayerId,
  setPlayerList,
  setScores,
  setSchedule,
  setSeating,
  setTournament,
  setPageIndex,
}

const DEBUG = true;

const String DEFAULT_COLOUR_KEY = 'black knight';

const Map<String, Color> BACKGROUND_COLOURS = {
  DEFAULT_COLOUR_KEY: Colors.black,
  'fireball red': Color(0xFF330000),
  'deep purple': Color(0xFF220033),
};

String dateRange(dynamic startDT, dynamic endDT) {
  if (startDT == null || endDT == null) return '';
  DateTime sd = startDT.toDate();
  DateTime ed = endDT.toDate();
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
  String end = DateFormat('HH:mm d MMM y').format(ed);
  return "$start - $end";
}

class ROUTES {
  static const String home = '/home';
  static const String privacyPolicy = '/privacyPolicy';
  static const String settings = '/settings';
  static const String tournaments = '/tournaments';
  static const String tournament = '/tournament';
}

const Color selectedHighlight = Color(0x88aaaaff);

enum Winds {
  east('E', '東'),
  south('S', '西'),
  west('W', '南'),
  north('N', '北');

  const Winds(this.western, this.japanese);

  final String japanese;
  final String western;
}

class Player extends Equatable implements Comparable<Player> {
  const Player(this.id, this.name);

  final int id;
  final String name;

  @override
  int compareTo(Player other) => name.compareTo(other.name);

  @override
  toString() => '$name ($id)';

  @override
  List<Object?> get props => [
        id,
        name,
      ];
}

extension PlayerList on List<Player> {
  Player? byId(int id) {
    try {
      return firstWhere((player) => player.id == id);
    } on StateError {
      return null;
    }
  }
}

typedef SeatingPlan = List<RoundState>;

extension RoundList on List<RoundState> {
  Iterable<RoundState> withPlayerId(int? playerId) => playerId == null
      ? this
      : map((round) => RoundState(
            id: round.id,
            tables: {
              for (final MapEntry(:key, :value) in round.tables.entries)
                if (value.contains(playerId)) key: value,
            },
          ));
}

class RoundState extends Equatable {
  const RoundState({
    required this.id,
    required this.tables,
  });

  factory RoundState.fromJson(Map<String, dynamic> data) => RoundState(
        id: data['id'],
        tables: (data['tables'] as Map).map(
          (key, value) => MapEntry(
            key,
            (value as List).cast(),
          ),
        ),
      );

  final String id;
  final Map<String, List<int>> tables;

  String tableNameForPlayerId(int playerId) =>
      tables.entries.firstWhere((e) => e.value.contains(playerId)).key;

  @override
  List<Object?> get props => [
        id,
        tables,
      ];
}

/// Get the seating for an individual player
/// [seating] is the seating plan for the whole tournament
/// [selected] is the player id
/// [getSeats] returns the SeatingPlan just for the player selected
SeatingPlan getSeats(SeatingPlan seating, int? selected) {
  return [
    for (final e in seating)
      RoundState(
        id: e.id,
        tables: {
          for (final MapEntry(:key, :value) in e.tables.entries)
            if (value.contains(selected)) key: [...value]
        },
      )
  ];
}

class Log {
  static List<List<dynamic>> logs = [];

  static void debug(String text) {
    debugPrint(text);
  }

  static void _saveLog(LOG type, String text) {
    String typeString = enumToString(type);
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

class RunOrQueue {
  FutureOr<void> Function()? current;
  FutureOr<void> Function()? next;

  Future<void> call(FutureOr<void> Function() block) async {
    if (current != null) {
      next = block;
      return;
    }
    current = block;
    while (current != null) {
      try {
        await current!();
      } finally {
        current = next;
        next = null;
      }
    }
  }
}
