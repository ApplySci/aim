/*

 Utility functions, enums and constants used across the app

 This should NEVER import things from elsewhere in the app.
 This is to avoid circular dependencies.

 */
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:firebase_messaging/firebase_messaging.dart';

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
  initPreferences,
  restoreFromJSON,
  setPlayerId,
  setPlayerList,
  setPreferences,
  setScores,
  setSeating,
  setTournament,
}

const DEBUG = true;

const String DEFAULT_COLOUR_KEY = 'black knight';

const Map<String, Color> BACKGROUND_COLOURS = {
  DEFAULT_COLOUR_KEY: Colors.black,
  'fireball red': Color(0xFF330000),
  'deep purple': Color(0xFF220033),
};

class ROUTES {
  static const String home = '/home';
  static const String players = '/players';
  static const String privacyPolicy = '/privacyPolicy';
  static const String seating = '/seating';
  static const String scoreTable = '/scoreTable';
  static const String settings = '/settings';
  static const String tournaments = '/tournaments';
}

const Color selectedHighlight = Color(0x88aaaaff);

const Map<String, String> WINDS = {
  'western': 'ESWN',
  'japanese': '東南西北',
};

class Player implements Comparable<Player> {
  int id = -99;
  String name = '';

  Player(this.id, this.name);

  @override
  int compareTo(Player other) => name.compareTo(other.name);

  @override
  toString() => '$name ($id)';
}

class GLOBAL {
  static bool nameIsNotUnique(String name) {
    for (Map<String, dynamic> player in allPlayers) {
      if (player['name'] == name) {
        return true;
      }
    }
    return false;
  }

  static String currentRouteName(BuildContext context) {
    String routeName = '';

    Navigator.popUntil(context, (route) {
      if (route.settings.name != null) {
        routeName = route.settings.name!;
      }
      return true;
    });

    return routeName;
  }

  static List<Map<String, dynamic>> allPlayers = [];
  static bool playersListUpdated = false;
  static int nextUnregisteredID = -2;
}

typedef SeatingPlan = List<Map<String, dynamic>>;

/// Get the seating for an individual player
/// [seating] is the seating plan for the whole tournament
/// [selected] is the player id
/// [getSeats] returns the SeatingPlan just for the player selected
SeatingPlan getSeats(SeatingPlan seating, int selected) {
  // deep-cloning this fairly simple object with JSON
  SeatingPlan theseSeats = SeatingPlan.from(jsonDecode(jsonEncode(seating)));
  for (int i=0; i < seating.length; i++) {
    seating[i]['tables'].forEach((String tableName, dynamic table) {
      if (!table.contains(selected)) {
        theseSeats[i]['tables'].remove(tableName);
      }
    });
  }
  return theseSeats;
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
