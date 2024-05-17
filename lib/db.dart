import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'package:alarm/alarm.dart';
import 'package:alarm/model/alarm_settings.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/timezone.dart' as tz;

import 'store.dart';
import 'utils.dart';

class DB {
  DB._();

  static final instance = DB._();
  final _db = FirebaseFirestore.instance;
  final Map _listeners = {};
  final GlobalKey<ScaffoldMessengerState> scaffoldMessengerKey =
      GlobalKey<ScaffoldMessengerState>();

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

  Stream<QuerySnapshot> getTournaments() {
    Stream<QuerySnapshot> docs;
    if (kDebugMode) {
      docs = _db.collection('tournaments').snapshots();
    } else {
      docs = _db
          .collection('tournaments')
          .where('status', isEqualTo: 'live')
          .snapshots();
    }
    return docs;
  }

  Future<List<int>> getAlarmIds() async {
    List<int> alarms = [];
    int alarmIdBase = store.state.tournament.hashCode.abs() % 1000000;
    int roundCount = store.state.seating.length;
    for (int i = 1; i <= roundCount; i++) {
      // a deterministic way to generate a unique-ish int from the google doc id
      alarms.add(10 * alarmIdBase + i);
    }
    return alarms;
  }

  final runOrQueue = RunOrQueue();
  Future<void> setAllAlarms() async {
    return runOrQueue(() => _setAllAlarms());
  }

  Future<void> _setAllAlarms() async {
    final now = DateTime.now().toUtc();
    final targetPlayer =
        store.state.playerMap.containsKey(store.state.selected);
    final seating = targetPlayer ? store.state.theseSeats : store.state.seating;
    final playerName =
        targetPlayer ? store.state.playerMap[store.state.selected] ?? '' : '';
    final schedule = store.state.schedule;
    final alarmIds = await getAlarmIds();
    final currentTimeZone = await FlutterTimezone.getLocalTimezone();

    await Alarm.stopAll();
    await Future.delayed(const Duration(milliseconds: 100));

    // set one alarm for each round
    for (final (index, round) in seating.indexed) {
      final name = round.id;
      final loc = tz.getLocation(currentTimeZone);
      final alarmTime = tz.TZDateTime.from(schedule!.hanchan[name]!.start, loc)
          .toLocal()
          .subtract(const Duration(minutes: 5));
      if (now.isBefore(alarmTime)) {
        final roundId = schedule.hanchan[name]!.name;
        final title = "$roundId starts in 5 minutes";
        final body = switch (targetPlayer) {
          true => "$playerName is on table ${round.tables.keys.first}",
          false => '',
        };
        await setAlarm(alarmTime, title, body, alarmIds[index]);
        await Future.delayed(const Duration(milliseconds: 100));
      }
    }
  }

  void getTournamentFromId(String docId) {
    if (docId.length < 5) return;
    _db.collection('tournaments').doc(docId).snapshots().listen(
      (event) {
        store.dispatch(SetTournamentAction(
          tournament: TournamentState.fromJson({
            'id': docId,
            ...event.data()!,
          }),
        ));
        listenToTournament(docId);
      },
      onError: (error) => Log.warn("Tournament-doc Listen failed: $error"),
    );
  }

  Future<void> listenToTournament(String docId) async {
    CollectionReference collection =
        _db.collection('tournaments').doc(docId).collection('json');

    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final actions = {
      'seating': const SetSeatingAction(seating: []),
      'schedule': SetScheduleAction(
        schedule: ScheduleState(timezone: tz.UTC, hanchan: {}),
      ),
      'scores': const SetScoresAction(scores: []),
      'players': const SetPlayerListAction(players: []),
    };
    for (var MapEntry(key: type, value: action) in actions.entries) {
      if (_listeners.containsKey(type)) {
        try {
          _listeners[type].cancel();
        } finally {}
      }

      _listeners[type] = collection.doc(type).snapshots().listen(
        (event) async {
          final eventData = event.data();
          if (eventData case {'json': dynamic json}) {
            final data = jsonDecode(json);
            action = switch (action) {
              SetSeatingAction() => SetSeatingAction.fromJson(data),
              SetScheduleAction() => SetScheduleAction.fromJson(data),
              SetScoresAction() => SetScoresAction.fromJson(data),
              SetPlayerListAction() => SetPlayerListAction.fromJson(data),
              _ => action,
            };
          }
          if (action case SetScheduleAction(schedule: final schedule)) {
            await setTimeZone(schedule);
            bool wantAlarms = prefs.getBool('alarm') ?? true;
            if (wantAlarms && store.state.schedule != null) {
              await setAllAlarms();
            }
          } else {
            store.dispatch(action);
          }

          // final ScaffoldMessengerState? state =
          //     scaffoldMessengerKey.currentState;
          // state?.showSnackBar(SnackBar(content: Text('$type updated')));
        },
        onError: (error) => Log.error("$type listener failed: $error"),
      );
    }
  }
}
