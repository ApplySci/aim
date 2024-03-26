/// Glues the whole thing together with variables shared app-wide, using redux
library;

import 'dart:convert';

import 'package:redux/redux.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'utils.dart';

late SharedPreferences _prefs;

const Map<String, dynamic> DEFAULT_PREFERENCES = {
  'backgroundColour': DEFAULT_COLOUR_KEY, // Colors.black,
  'japaneseWinds': false,
  'japaneseNumbers': false,
  'serverUrl': 'https://tournaments.mahjong.ie/',
  'tournament': 'cork2024',
  'playerId': -1, // id of player being focused on
};


class AllState {
  bool loadedOK = false;
  List<Map<String, dynamic>> scores = [];
  List<Player> players = [];
  Map<int, String> playerMap = {};
  int rounds = 5;
  int roundDone = 0;
  int selected = -1;
  SeatingPlan theseSeats=[], seating=[];
  String tournament = 'cork2024';
  Map<String, dynamic> preferences = Map.from(DEFAULT_PREFERENCES);
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
      var incoming = action['players'];
      if (incoming is Map) {
        List<Player> players = [];
        incoming.forEach((k, v) {
          players.add(Player(k is int ? k : int.parse(k), v));
        });
        state.players = players;
      } else {
        state.players = incoming;
      }
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
      state.scores = List<Map<String,dynamic>>.from(action['scores']);
      if (state.scores.isNotEmpty) {
        state.roundDone = state.scores[0].containsKey('roundDone')
            ? state.scores[0]['roundDone']
            : 0;
      } else {
        state.roundDone = 0;
      }
      break;

    case STORE.setSeating:
      state.seating = SeatingPlan.from(action['seating']);
      if (state.selected >= 0) {
        state.theseSeats = getSeats(state.seating, state.selected);
      }
      break;

    case STORE.setTournament:
      state.tournament = action['tournament'];
      // TODO get data for this tourney now
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
