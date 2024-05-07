/// Glues the whole thing together with variables shared app-wide, using redux
library;

import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:redux/redux.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest_10y.dart' as tz;
import 'utils.dart';

late SharedPreferences prefs;

Future<void> setTimeZone(newSchedule) async {
  tz.Location loc;
  bool useEventTimeZone = prefs.getBool('tz') ?? true;
  if (useEventTimeZone) {
    dynamic test = newSchedule['timezone'];
    loc = test is tz.Location ? test : tz.getLocation(test);
  } else {
    // using the device timezone
    String currentTimeZone = await FlutterTimezone.getLocalTimezone();
    loc = tz.getLocation(currentTimeZone);
  }
  tz.setLocalLocation(loc);
  newSchedule.forEach((key, value) {
    if (key != "timezone") {
      dynamic thisStart = value['start'];
      if (thisStart is String) {
        // convert it to a UTC DateTime
        thisStart = DateTime.parse(thisStart);
      } // and if it's not a string, it's already a tz.TZDateTime
      newSchedule[key]['start'] = tz.TZDateTime.from(thisStart, tz.local);
    }
  });
  store.dispatch({
    'type': STORE.setSchedule,
    'schedule': newSchedule,
  });
}

Future<void> initPrefs() async {
  prefs = await SharedPreferences.getInstance();
  store.dispatch({
    'type': STORE.setPlayerId,
    'playerId': prefs.getInt('selected') ?? -2,
  });
  tz.initializeTimeZones();
}


class AllState {
  bool loadedOK = false;
  List<Map<String, dynamic>> scores = [];
  List<Player> players = [];
  Map<int, String> playerMap = {};
  int roundDone = 0;
  int selected = -1;
  SeatingPlan theseSeats=[];
  SeatingPlan seating=[];
  Map<String, dynamic> schedule={};
  String tournamentId = "Y3sDqxajiXefmP9XBTvY";  // google document id
  Map<String, dynamic> tournament = {
    'name': 'No tournament selected yet',
    'address': '',
  };
}


/// Sole arbiter of the contents of the Store after initialisation
AllState stateReducer(AllState state, dynamic action) {

  // Log.debug(action.toString()); // for debugging all STORE actions

  STORE toDo = action is STORE ? action : action['type'];

  switch (toDo) {

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

    case STORE.setSchedule:
      state.schedule = Map<String, dynamic>.from(action['schedule']);
      state.schedule['timezone'] = tz.getLocation(state.schedule['timezone']);
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
