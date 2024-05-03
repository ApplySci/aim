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
      volume: 0.8,
      fadeDuration: 0.1,
      notificationTitle: title,
      notificationBody: body,
      enableNotificationOnKill: true,
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

  void setAllAlarms() async {
    DateTime now = DateTime.now().toUtc();
    int roundNumber = 1;
    String body;
    String tableName;
    String roundId;
    String title;
    // a deterministic way to generate a unique-ish int from the google doc id:
    int alarmIdBase = store.state.tournament.hashCode.abs() % 1000000;
    bool targetPlayer = store.state.playerMap.containsKey(store.state.selected);
    SeatingPlan seating = targetPlayer ? List.from(store.state.theseSeats)
        : List.from(store.state.seating);
    String playerName = targetPlayer
        ? store.state.playerMap[store.state.selected] ?? ''
        : '';
    Map schedule = Map.from(store.state.schedule);
    // set one alarm for each round
    for (Map round in seating) {
      String name = round['id'];
      String currentTimeZone = await FlutterTimezone.getLocalTimezone();
      tz.Location loc = tz.getLocation(currentTimeZone);
      DateTime alarmTime = tz.TZDateTime.from(schedule[name]['start'], loc)
        .toLocal()
        .subtract(const Duration(minutes: 5));
      int alarmId = 10 * alarmIdBase + roundNumber;
      roundNumber += 1;
      if (now.isBefore(alarmTime)) {
        roundId = schedule[name]['name'];
        title = "$roundId starts in 5 minutes";
        if (targetPlayer) {
          tableName = round['tables'].keys.first;
          body = "$playerName is on table $tableName";
        } else {
          body = '';
        }
        setAlarm(alarmTime, title, body, alarmId);
      }
    }
  }

  void getTournamentFromId(String docId) {
    if (docId.length < 5) return;
    _db.collection('tournaments').doc(docId).snapshots().listen(
      (event) {
        store.dispatch({
          'type': STORE.setTournament,
          'tournamentId': docId,
          'tournament': event.data(),
        });
        listenToTournament(docId);
      },
      onError: (error) => Log.warn("Tournament-doc Listen failed: $error"),
    );
  }


  Future<void> listenToTournament(String docId) async {
  CollectionReference collection = _db.collection('tournaments').doc(docId)
        .collection('json');

    List jsons = [
      [
        'seating',        // field name
        STORE.setSeating, // Store update type
        <SeatingPlan>[],  // default value
      ],
      [
        'schedule',
        STORE.setSchedule,
        <String,String>{},
      ],
      [
        'scores',
        STORE.setScores,
        <Map<String,dynamic>>[],
      ],
      [
        'players',
        STORE.setPlayerList,
        <Player>[],
      ],
    ];
    for (List json in jsons) {
      if (_listeners.containsKey(json[0])) {
        try {
          _listeners[json[0]].cancel();
        } finally {}
      }

      _listeners[json[0]] = collection.doc(json[0]).snapshots().listen(
        (event) async {
          SharedPreferences prefs = await SharedPreferences.getInstance();
          dynamic eventData = event.data();
          dynamic newValue;
          if (eventData == null || ! eventData.containsKey('json')) {
            newValue = json[2];
          } else {
            newValue = jsonDecode(eventData['json']);
          }
          if (json[0] == "schedule") {
            await setTimeZone(newValue);
            bool wantAlarms = prefs.getBool('alarm') ?? true;
            if (wantAlarms && store.state.schedule.isNotEmpty) {
              setAllAlarms();
            }
          } else {
            store.dispatch({
              'type': json[1],
              json[0]: newValue,
            });
          }
          final ScaffoldMessengerState? state =
              scaffoldMessengerKey.currentState;
          state?.showSnackBar(SnackBar(content: Text('${json[0]} updated')));
        },
        onError: (error) => Log.error("${json[0]} listener failed: $error"),
      );
    }
  }
}
