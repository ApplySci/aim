/// Glues the whole thing together with variables shared app-wide, using redux
library;

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:equatable/equatable.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:redux/redux.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest_10y.dart' as tz;
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/timezone.dart';

import 'db.dart';
import 'fcm_client.dart';
import 'utils.dart';

late SharedPreferences prefs;

Future<void> setTimeZone(ScheduleState newSchedule) async {
  final useEventTimeZone = prefs.getBool('tz') ?? true;
  final loc = switch (useEventTimeZone) {
    true => newSchedule.timezone,
    false => tz.getLocation(await FlutterTimezone.getLocalTimezone()),
  };
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

class AllState extends Equatable {
  const AllState({
    required this.tournament,
    required this.schedule,
    required this.players,
    required this.scores,
    required this.seating,
    required this.roundDone,
    required this.selected,
  });

  final TournamentState? tournament;
  final ScheduleState? schedule;
  final List<Player> players;
  final List<ScoreState> scores;
  final SeatingPlan seating;
  final int roundDone;
  final int? selected;

  @override
  List<Object?> get props => [
        tournament,
        schedule,
        players,
        scores,
        seating,
        roundDone,
        selected,
      ];
}

class ScoreState extends Equatable {
  const ScoreState({
    required this.id,
    required this.rank,
    required this.total,
    required this.penalty,
    required this.roundScores,
    required this.roundDone,
  });

  factory ScoreState.fromJson(Map<String, dynamic> data) => ScoreState(
        id: data['id'],
        rank: data['r'],
        total: data['t'],
        penalty: data['p'],
        roundScores: (data['s'] as List).cast(),
        roundDone: data['roundDone'] ?? 0,
      );

  final int id;
  final String rank;
  final int total;
  final int penalty;
  final List<int> roundScores;
  final int roundDone;

  @override
  List<Object?> get props => [
        id,
        rank,
        total,
        penalty,
        roundScores,
        roundDone,
      ];
}

class ScheduleState extends Equatable {
  const ScheduleState({
    required this.timezone,
    required this.rounds,
  });

  factory ScheduleState.fromJson(Map<String, dynamic> data) => ScheduleState(
        timezone: tz.getLocation(data['timezone']),
        rounds: {
          for (final MapEntry(:key, :value) in data.entries)
            if (key != 'timezone') key: RoundSchedule.fromJson(value),
        },
      );

  final Location timezone;
  final Map<String, RoundSchedule> rounds;

  @override
  List<Object?> get props => [
        timezone,
        rounds,
      ];
}

class RoundSchedule extends Equatable {
  const RoundSchedule({
    required this.name,
    required this.start,
  });

  factory RoundSchedule.fromJson(Map<String, dynamic> data) => RoundSchedule(
        name: data['name'],
        start: tz.TZDateTime.from(DateTime.parse(data['start']), tz.local),
      );

  final String name;
  final DateTime start;

  @override
  List<Object?> get props => [
        name,
        start,
      ];
}

class TournamentState extends Equatable {
  const TournamentState({
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

  @override
  List<Object?> get props => [
        id,
        name,
        address,
        country,
        startDate,
        endDate,
        status,
        rules,
      ];
}

/// Sole arbiter of the contents of the Store after initialisation
AllState stateReducer(AllState state, dynamic action) {
  // Log.debug(action.toString()); // for debugging all STORE actions

  switch (action) {
    case SetPlayerIdAction():
      if (action.playerId case int selected) {
        prefs.setInt('selected', selected);
      } else {
        prefs.remove('selected');
      }

      return AllState(
        tournament: state.tournament,
        schedule: state.schedule,
        players: state.players,
        scores: state.scores,
        seating: state.seating,
        roundDone: state.roundDone,
        selected: action.playerId,
      );

    case SetPlayerListAction():
      return AllState(
        tournament: state.tournament,
        schedule: state.schedule,
        players: action.players,
        scores: state.scores,
        seating: state.seating,
        roundDone: state.roundDone,
        selected: state.selected,
      );

    case SetScheduleAction():
      return AllState(
        tournament: state.tournament,
        schedule: action.schedule,
        players: state.players,
        scores: state.scores,
        seating: state.seating,
        roundDone: state.roundDone,
        selected: state.selected,
      );

    case SetScoresAction():
      return AllState(
        tournament: state.tournament,
        schedule: state.schedule,
        players: state.players,
        scores: action.scores,
        seating: state.seating,
        roundDone: state.roundDone,
        selected: state.selected,
      );

    case SetSeatingAction():
      return AllState(
        tournament: state.tournament,
        schedule: state.schedule,
        players: state.players,
        scores: state.scores,
        seating: action.seating,
        roundDone: state.roundDone,
        selected: state.selected,
      );

    case SetTournamentAction():
      subscribeToTopic(action.tournament.id, action.tournament.id);
      DB.instance.listenToTournament(action.tournament.id);
      prefs.setString('tournamentId', action.tournament.id);

      return AllState(
        tournament: action.tournament,
        schedule: state.schedule,
        players: state.players,
        scores: state.scores,
        seating: state.seating,
        roundDone: state.roundDone,
        selected: state.selected,
      );
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

/// global variables are bad. But incredibly useful here.
final store = Store<AllState>(
  stateReducer,
  initialState: const AllState(
    tournament: null,
    schedule: null,
    players: [],
    scores: [],
    seating: [],
    roundDone: 0,
    selected: null,
  ),
);
