import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'package:alarm/alarm.dart';
import 'package:alarm/model/alarm_settings.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'store.dart';
import 'utils.dart';

class DB {
  DB._();

  static final instance = DB._();
  final _db = FirebaseFirestore.instance;
  final DateFormat _dateFormat = DateFormat("EEEE dd MMMM yyyy, HH:mm");
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

  void setAllAlarms() {
    // TODO check behaviour with mixed timezones!
    DateTime now = DateTime.now().toUtc();
    int roundNumber = 1;
    String body;
    String tableName;
    String roundId;
    String title;
    // a deterministic way to generate a unique-ish int from the google doc id:
    int alarmIdBase = store.state.tournament.hashCode.abs() % 1000000;
    bool targetPlayer = store.state.playerMap.containsKey(store.state.selected);
    SeatingPlan seating = targetPlayer ? store.state.theseSeats
        : store.state.seating;
    String playerName = targetPlayer
        ? store.state.playerMap[store.state.selected] ?? ''
        : '';
    // set one alarm for each round
    for (Map round in seating) {
      Log.debug("Hanchan start time: ${round['start']}");
      DateTime alarmTime =
        _dateFormat.parse(round['start']).subtract(const Duration(minutes: 5));
      int alarmId = 10 * alarmIdBase + roundNumber;
      roundNumber += 1;
      if (now.isBefore(alarmTime)) {
        roundId = round['id'];
        title = "Hanchan $roundId starts in 5 minutes";
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
        'scores',
        STORE.setScores,
        <List<Map<String,dynamic>>>[],
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
          bool inSeating = json[0] == "seating";
          bool wantAlarms = prefs.getBool('alarm') ?? true;
          dynamic eventData = event.data();
          dynamic newValue;
          if (eventData == null || ! eventData.containsKey('json')) {
            newValue = json[2];
          } else {
            newValue = jsonDecode(eventData['json']);
          }
          store.dispatch({
            'type': json[1],
            json[0]: newValue,
          });
          if (inSeating && wantAlarms) {
            setAllAlarms();
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
