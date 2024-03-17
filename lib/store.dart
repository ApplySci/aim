/// Glues the whole thing together with variables shared app-wide, using redux
library;

import 'dart:convert';

import 'package:redux/redux.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

import 'utils.dart';

late SharedPreferences _prefs;

const Map<String, dynamic> DEFAULT_PREFERENCES = {
  'backgroundColour': DEFAULT_COLOUR_KEY, // Colors.black,
  'japaneseWinds': false,
  'japaneseNumbers': false,
  'serverUrl': 'https://tournaments.mahjong.ie/',
  'playerId': -1, // id of player being focused on
  'tournament': 'cork2024',
};

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

class AllState {
  bool loadedOK = false;
  List<Map<String, dynamic>> scores = [];
  List<Player> players = [];
  Map<int, String> playerMap = {};
  int rounds = 5;
  int roundDone = 0;
  int selected = -1;
  SeatingPlan theseSeats=[], seating=[];

  Map<String, dynamic> preferences = Map.from(DEFAULT_PREFERENCES);

  String toJSON() {
    // TODO save AllState data to local storage
    Map<String, dynamic> valuesToSave = {
      'scores': scores,
      'players': players,
      'rounds': rounds,
      'selected': selected,
      'seating': seating,
    };
    return jsonEncode(valuesToSave);
  }
}

/// Sole arbiter of the contents of the Store after initialisation
AllState stateReducer(AllState state, dynamic action) {
  void fromJSON(String json) {
    Map<String, dynamic> restoredValues = jsonDecode(json);

    Log.logs = List<List<dynamic>>.from(restoredValues['log']);
    state.scores = <Map<String, dynamic>>[];
    (restoredValues['scores'] as Map<String, dynamic>)
        .forEach((String key, dynamic values) {});
  }

  Log.debug(action.toString()); // for debugging all STORE actions

  STORE toDo = action is STORE ? action : action['type'];

  switch (toDo) {
    case STORE.initPreferences:
      action['preferences'].forEach((key, val) {
        state.preferences[key] = val;
      });
      break;

    case STORE.restoreFromJSON:
      try {
        fromJSON(action['json']);
        state.loadedOK = true;
      } catch (e, stackTrace) {
        Log.error('failed to restore game: $e , $stackTrace');
        state.loadedOK = false;
      }
      break;

    case STORE.setPlayerId:
      state.selected = action['playerId'];
      state.theseSeats = getSeats(state.seating, state.selected);
      break;

    case STORE.setPlayerList:
      state.players = action['players'];
      state.playerMap = {for (Player p in state.players) p.id: p.name};
      break;

    case STORE.setPreferences:
      action['preferences'].forEach((key, val) {
        state.preferences[key] = val;
        if (val is bool) {
          _prefs.setBool(key, val);
        } else if (val is String) {
          _prefs.setString(key, val);
        } else if (val is double) {
          _prefs.setDouble(key, val);
        } else if (val is int) {
          _prefs.setInt(key, val);
        }
      });
      break;

    case STORE.setScores:
      state.scores = action['scores'];
      break;

    case STORE.setSeating:
      state.seating = SeatingPlan.from(action['seating']);
      if (state.seating.isNotEmpty) {
        state.roundDone = state.seating[0]['roundDone'];
      } else {
        state.roundDone = 0;
      }
      if (state.selected >= 0) {
        state.theseSeats = getSeats(state.seating, state.selected);
      }
      break;

    case STORE.setTournament:
      break;
  }

  return state;
}

/// Initialise preferences, using defaults and values from disk
Future initPrefs() {
  return SharedPreferences.getInstance().then((SharedPreferences prefs) {
    _prefs = prefs;
    final Map prefsFromDisk = {
      'type': STORE.initPreferences,
      'preferences': {}
    };
    store.state.preferences.forEach((key, val) {
      dynamic test = _prefs.get(key);
      if (test != null && test != val) {
        prefsFromDisk['preferences'][key] = test;
      }
    });
    if (prefsFromDisk['preferences'].length > 0) {
      store.dispatch(prefsFromDisk);
    }
  });
}

/// global variables are bad. But incredibly useful here.
final store = Store<AllState>(
  stateReducer,
  initialState: AllState(),
);
