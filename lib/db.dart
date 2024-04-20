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
    int id, // TODO something we can derive from tourney id and hanchan number
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

  void setAllAlarms(SeatingPlan seating) {
    DateTime now = DateTime.now().toUtc();
    String? playerName;

    if (store.state.selected >= 0) {
      playerName = store.state.playerMap[store.state.selected];
    }
    int roundNumber = 1;
    String body;
    String tableName;
    String roundId;
    String title;
    int alarmIdBase = store.state.tournament.hashCode.abs() % 1000000;
    for (Map round in seating) {
      Log.debug("Hanchan start time: ${round['start']}");
      DateTime alarmTime =
        _dateFormat.parse(round['start']).subtract(const Duration(minutes: 5));
      int alarmId = 10 * alarmIdBase + roundNumber;
      roundNumber += 1;
      if (now.isBefore(alarmTime)) {
        // generate alarm id from tournament name and hanchan number
        roundId = round['id'];
        title = "Hanchan $roundId starts in 5 minutes";
        if (store.state.selected >= 0) {
          String playerName = store.state.playerMap[store.state.selected]!;
          tableName = store.state.theseSeats[roundNumber]['tables'].keys.first;
          body = "$playerName is on table $tableName";
        } else {
          body = '';
        }
        setAlarm(alarmTime, title, body, alarmId);
      }
    }
  }

  Future<void> getTournament(DocumentSnapshot t, Map tData) async {
    String id = t.id;
    store.dispatch({
      'type': STORE.setTournament,
      'tournament': id,
      'tournamentName': tData['name'],
      'tournamentAddress': tData['address'],
    });
    var collection = _db.collection('tournaments').doc(id).collection('json');

    List jsons = [
      [
        'seating',
        STORE.setSeating,
      ],
      [
        'scores',
        STORE.setScores,
      ],
      [
        'players',
        STORE.setPlayerList,
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
          store.dispatch({
            'type': json[1],
            json[0]: jsonDecode(event.data()!['json']),
          });
          if (inSeating && wantAlarms) {
            setAllAlarms(store.state.seating);
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
