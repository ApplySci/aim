// utility functions, enums and constants used across the app
import 'package:flutter/material.dart';


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
  setPlayerList,
  setPreferences,
  setScores,
  setTournament,
}

const String DEFAULT_COLOUR_KEY = 'black knight';

const Map<String, Color> BACKGROUND_COLOURS = {
  DEFAULT_COLOUR_KEY: Colors.black,
  'fireball red': Color(0xFF330000),
  'deep purple': Color(0xFF220033),
};

class ROUTES {
  static const String help = '/help';
  static const String liveGames = '/games/live';
  static const String privacyPolicy = '/privacyPolicy';
  static const String settings = '/settings';
  static const String scoreSheet = '/scoresheet';
  static const String welcome = '/welcome';
}

const Map<String, String> WINDS = {
  'western': 'ESWN',
  'japanese': '東南西北',
};

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
    String routeName='';

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
