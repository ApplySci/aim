/// Glues the whole thing together with variables shared app-wide, using redux
library;

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:redux/redux.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest_10y.dart' as tz;
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/timezone.dart';

import 'utils.dart';

late SharedPreferences prefs;

Future<void> setTimeZone(ScheduleState newSchedule) async {
  tz.Location loc;
  bool useEventTimeZone = prefs.getBool('tz') ?? true;
  if (useEventTimeZone) {
    dynamic test = newSchedule.timezone;
    loc = test is tz.Location ? test : tz.getLocation(test);
  } else {
    // using the device timezone
    String currentTimeZone = await FlutterTimezone.getLocalTimezone();
    loc = tz.getLocation(currentTimeZone);
  }
  tz.setLocalLocation(loc);
  store.dispatch(SetScheduleAction(schedule: newSchedule));
}

Future<void> initPrefs() async {
  prefs = await SharedPreferences.getInstance();
  store.dispatch(SetPlayerIdAction(
    playerId: prefs.getInt('selected'),
  ));
  tz.initializeTimeZones();
}

class AllState {
  bool loadedOK = false;
  List<ScoreState> scores = [];
  List<Player> players = [];
  Map<int, String> playerMap = {};
  int roundDone = 0;
  int? selected;
  SeatingPlan theseSeats = [];
  SeatingPlan seating = [];
  ScheduleState? schedule;
  String tournamentId = "Y3sDqxajiXefmP9XBTvY"; // google document id
  TournamentState? tournament;
  int pageIndex = 0;
}

class ScoreState {
  const ScoreState({
    required this.id,
    required this.r,
    required this.t,
    required this.p,
    required this.s,
    required this.roundDone,
  });

  factory ScoreState.fromJson(Map<String, dynamic> data) => ScoreState(
        id: data['id'],
        r: data['r'],
        t: data['t'],
        p: data['p'],
        s: (data['s'] as List).cast(),
        roundDone: data['roundDone'] ?? 0,
      );

  final int id;
  final String r;
  final int t;
  final int p;
  final List<int> s;
  final int roundDone;
}

class ScheduleState {
  const ScheduleState({
    required this.timezone,
    required this.hanchan,
  });

  factory ScheduleState.fromJson(Map<String, dynamic> data) => ScheduleState(
        timezone: tz.getLocation(data['timezone']),
        hanchan: {
          for (final MapEntry(:key, :value) in data.entries)
            if (key != 'timezone') key: HanchanSchedule.fromJson(value),
        },
      );

  final Location timezone;
  final Map<String, HanchanSchedule> hanchan;
}

class HanchanSchedule {
  HanchanSchedule({
    required this.name,
    required this.start,
  });

  factory HanchanSchedule.fromJson(Map<String, dynamic> data) =>
      HanchanSchedule(
        name: data['name'],
        start: tz.TZDateTime.from(DateTime.parse(data['start']), tz.local),
      );

  final String name;
  final DateTime start;
}

class TournamentState {
  TournamentState({
    required this.id,
    required this.name,
    required this.address,
    required this.country,
    required this.startDate,
    required this.endDate,
    required this.status,
    required this.rules,
  });

  factory TournamentState.fromJson(Map<String, dynamic> data) =>
      TournamentState(
        id: data['id'],
        name: data['name'],
        address: data['address'],
        country: data['country'],
        startDate: data['start_date'],
        endDate: data['end_date'],
        status: data['status'],
        rules: data['rules'],
      );

  final String id;
  final String name;
  final String address;
  final String country;
  final Timestamp startDate;
  final Timestamp endDate;
  final String status;
  final String rules;
}

/// Sole arbiter of the contents of the Store after initialisation
AllState stateReducer(AllState state, StateAction action) {
  // Log.debug(action.toString()); // for debugging all STORE actions

  switch (action) {
    case SetPlayerIdAction():
      state.selected = action.playerId;
      state.theseSeats = getSeats(state.seating, state.selected);
      if (state.selected case int selected) {
        prefs.setInt('selected', selected);
      } else {
        prefs.remove('selected');
      }
      break;

    case SetPlayerListAction():
      state.players = action.players;
      state.playerMap = {for (Player p in state.players) p.id: p.name};
      break;

    case SetScheduleAction():
      state.schedule = action.schedule;
      break;

    case SetScoresAction():
      state.scores = action.scores;
      if (state.scores.isNotEmpty) {
        state.roundDone = state.scores[0].roundDone;
      } else {
        state.roundDone = 0;
      }
      break;

    case SetSeatingAction():
      state.seating = action.seating;
      if (state.selected case int selected) {
        state.theseSeats = getSeats(state.seating, selected);
      }
      break;

    case SetTournamentAction():
      state.tournament = action.tournament;
      prefs.setString('tournamentId', action.tournament.id);
      break;

    case SetPageIndexAction():
      state.pageIndex = action.pageIndex;
      break;
  }

  return state;
}

sealed class StateAction {
  const StateAction();
}

class SetPlayerIdAction extends StateAction {
  const SetPlayerIdAction({
    required this.playerId,
  });

  final int? playerId;
}

class SetPlayerListAction extends StateAction {
  const SetPlayerListAction({
    required this.players,
  });

  factory SetPlayerListAction.fromJson(Map data) => SetPlayerListAction(
        players: (data as Map<String, dynamic>)
            .entries
            .map((e) => Player(int.parse(e.key), e.value))
            .toList(),
      );

  final List<Player> players;
}

class SetScheduleAction extends StateAction {
  const SetScheduleAction({
    required this.schedule,
  });

  factory SetScheduleAction.fromJson(Map<String, dynamic> data) =>
      SetScheduleAction(schedule: ScheduleState.fromJson(data));

  final ScheduleState schedule;
}

class SetScoresAction extends StateAction {
  const SetScoresAction({
    required this.scores,
  });

  factory SetScoresAction.fromJson(List<dynamic> data) => SetScoresAction(
        scores: data.map((e) => ScoreState.fromJson(e)).toList(),
      );

  final List<ScoreState> scores;
}

class SetSeatingAction extends StateAction {
  const SetSeatingAction({
    required this.seating,
  });

  factory SetSeatingAction.fromJson(List data) => SetSeatingAction(
        seating: data.map((e) => RoundState.fromJson(e)).toList(),
      );

  final SeatingPlan seating;
}

class SetTournamentAction extends StateAction {
  const SetTournamentAction({
    required this.tournament,
  });

  final TournamentState tournament;
}

class SetPageIndexAction extends StateAction {
  const SetPageIndexAction({
    required this.pageIndex,
  });

  final int pageIndex;
}

/// global variables are bad. But incredibly useful here.
final store = Store<AllState>(
  (state, action) => stateReducer(state, action),
  initialState: AllState(),
);
