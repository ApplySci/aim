import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'package:alarm/alarm.dart';
import 'package:alarm/model/alarm_settings.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
      SharedPreferences prefs
      ) async {

    final alarmSettings = AlarmSettings(
      id: 42, // something we can store or derive, based on tourney id and hanchan number
      dateTime: when,
      assetAudioPath: 'assets/alarm.mp3', // TODO
      loopAudio: false,
      vibrate: true,
      volume: 0.8,
      fadeDuration: 3.0,
      notificationTitle: title,
      notificationBody: title,
      enableNotificationOnKill: true,
    );

    // TODO we actually want to store an array of alarm ids
    await Alarm.set(alarmSettings: alarmSettings);

  }

  // setAlarm(when, prefs);
  // int id = await getAlarmId();
  // Alarm.stop(id);

  Stream<QuerySnapshot> getTournaments() {
    Stream<QuerySnapshot> docs;
    if (kDebugMode) {
      docs = _db.collection('tournaments').snapshots();
    } else {
      docs = _db.collection('tournaments')
          .where('status', isEqualTo: 'live').snapshots();
    }
    return docs;
  }

  void setAlarms(SeatingPlan oldSeating, SeatingPlan newSeating) {

  }

  Future<void> getTournament(DocumentSnapshot t) async {
    String id = t.id;
    store.dispatch({
      'type': STORE.setTournament,
      'tournament': id,
    });
    var collection = _db.collection('tournaments').doc(id).collection('json');

    List jsons = [
      ['seating', STORE.setSeating,],
      ['scores', STORE.setScores,],
      ['players', STORE.setPlayerList,],
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
          if (inSeating && wantAlarms) {
            // TODO setAlarms(store.state.seating
          }
          store.dispatch({
            'type': json[1],
            json[0]: jsonDecode(event.data()!['json']),
          });
          final ScaffoldMessengerState? state = scaffoldMessengerKey.currentState;
          state?.showSnackBar(
              SnackBar(content: Text('${json[0]} updated')));
        },
        onError: (error) => Log.error("${json[0]} listener failed: $error"),
      );
    }
  }
}
