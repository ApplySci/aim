import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';

import 'store.dart';
import 'utils.dart';

class DB {
  DB._();
  static final instance = DB._();
  final _db = FirebaseFirestore.instance;
  List _listeners = [];

  Stream<QuerySnapshot> getTournaments() {
    return _db.collection('tournaments').snapshots();
  }

  Future<void> getTournament(DocumentSnapshot t) async {
    String id = t.id;
    store.dispatch({
      'type': STORE.setTournament,
      'tournament': id,
    });
    _db.collection('tournaments').doc(id).collection('json').get().then(
      (snap) {
        Log.debug("Got json for tournament $id");
        for (var doc in snap.docs) {
          switch (doc.id) {
            case 'seating':
              store.dispatch({
                'type': STORE.setSeating,
                'seating': jsonDecode(doc.data()['json']),
              });
              break;
            case 'players':
              store.dispatch({
                'type': STORE.setPlayerList,
                'players': jsonDecode(doc.data()['json']),
              });
              break;
            case 'scores':
              store.dispatch({
                'type': STORE.setScores,
                'scores': List<Map<String, dynamic>>.from(
                    jsonDecode(doc.data()['json'])),
              });
              break;
          }
        }
      },
      onError: (e) => Log.error("Error in getTournament completing: $e"),
    );
    /* TODO implement listeners
    final listener = docRef.snapshots().listen(
          (event) => print("current data: ${event.data()}"),
          onError: (error) => print("Listen failed: $error"),
        );

    ...
    listener.cancel();
    */
  }
}
