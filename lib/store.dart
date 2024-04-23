/// Glues the whole thing together with variables shared app-wide, using redux
library;

import 'dart:convert';

import 'package:redux/redux.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'utils.dart';

late SharedPreferences prefs;

Future<void> initPrefs() async {
  prefs = await SharedPreferences.getInstance();
  store.dispatch({
    'type': STORE.setPlayerId,
    'playerId': prefs.getInt('selected') ?? -2,
  });
}

const Map<String, dynamic> DEFAULT_PREFERENCES = {
  'backgroundColour': DEFAULT_COLOUR_KEY, // Colors.black,
  'japaneseWinds': false,
  'japaneseNumbers': false,
  'serverUrl': 'https://tournaments.mahjong.ie/',
  'todo': [],
  'tournamentId': "Y3sDqxajiXefmP9XBTvY",
  'playerId': -1, // id of player being focused on
};


class AllState {
  bool loadedOK = false;
  List<Map<String, dynamic>> scores = [];
  List<Player> players = [];
  Map<int, String> playerMap = {};
  int roundDone = 0;
  int selected = -1;
  SeatingPlan theseSeats=[];
  SeatingPlan seating=[];
  String tournamentId = "Y3sDqxajiXefmP9XBTvY";  // google document id
  Map<String, dynamic> tournament = {
    'name': 'No tournament selected yet',
    'address': '',
  };
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
      prefs.setInt('selected', state.selected);
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
      state.tournament = Map.from(action['tournament']);
      if (state.tournament.containsKey('json')) {
        state.tournament.remove('json');
      }
      state.tournament['id'] = action['tournamentId'];
      prefs.setString('tournamentId', action['tournamentId']);
      break;

  }

  return state;
}

/// global variables are bad. But incredibly useful here.
final store = Store<AllState>(
  stateReducer,
  initialState: AllState(),
);
