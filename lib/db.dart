import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'package:cloud_firestore/cloud_firestore.dart';

import 'store.dart';
import 'utils.dart';

class DB {
  DB._();
  static final instance = DB._();
  final _db = FirebaseFirestore.instance;
  final Map _listeners = {};
  final GlobalKey<ScaffoldMessengerState> scaffoldMessengerKey =
    GlobalKey<ScaffoldMessengerState>();

  Stream<QuerySnapshot> getTournaments() {
    Stream<QuerySnapshot> docs;
    Log.debug('kDebugMode is $kDebugMode');
    if (kDebugMode) {
      docs = _db.collection('tournaments').snapshots();
    } else {
      docs = _db.collection('tournaments')
          .where('status', isEqualTo: 'live').snapshots();
    }
    return docs;
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
            (event) {
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
