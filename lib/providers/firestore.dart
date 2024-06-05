import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:collection/collection.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timezone/timezone.dart';

import '/models.dart';
import 'shared_preferences.dart';

T? snapshotData<T>(DocumentSnapshot<Map<String, dynamic>> snapshot) {
  if (snapshot.data() case {'json': String json}) {
    return jsonDecode(json) as T;
  }
  return null;
}

final firebaseProvider = Provider((ref) => FirebaseFirestore.instance);

final tournamentListProvider = StreamProvider((ref) {
  final db = ref.watch(firebaseProvider);
  final snapshots = switch (kDebugMode) {
    true => db.collection('tournaments').snapshots(),
    false => db
        .collection('tournaments')
        .where('status', isEqualTo: 'live')
        .snapshots(),
  };

  return snapshots.map((query) => [
        for (final doc in query.docs)
          TournamentData.fromJson({
            'id': doc.id,
            'address': '',
            ...(doc.data() as Map).cast(),
          }),
      ]);
});

final tournamentProvider = StreamProvider<TournamentData>((ref) async* {
  final db = ref.watch(firebaseProvider);
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return;

  yield* db
      .collection('tournaments')
      .doc(tournamentId)
      .snapshots()
      .map((snapshot) => TournamentData.fromJson({
            'id': snapshot.id,
            'address': '',
            ...(snapshot.data() as Map).cast(),
          }));
});

final tournamentCollectionProvider = Provider((ref) {
  final db = ref.watch(firebaseProvider);
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return null;

  return db.collection('tournaments').doc(tournamentId).collection('v2');
});

final playerListProvider = StreamProvider<List<PlayerData>>((ref) async* {
  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection
      .doc('players')
      .snapshots()
      .map((DocumentSnapshot<Map<String, dynamic>> snapshot) {
          Map<String, dynamic> data = snapshot.data() ?? {};
          if (data.containsKey('players')) {
            return [for (final Map<String, dynamic> player in data['players'])
                    PlayerData(player.cast())];
          } else {
            return [];
          }
        });
  }
);

final selectedPlayerProvider = Provider((ref) {
  final selectedPlayerId = ref.watch(selectedPlayerIdProvider);
  if (selectedPlayerId == null) return null;

  final playerList = ref.watch(playerListProvider).valueOrNull;
  return playerList
      ?.firstWhereOrNull((player) => player.id == selectedPlayerId);
});

final rankingProvider = StreamProvider<List<RankData>>((ref) async* {
  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection
      .doc('ranking')
      .snapshots()
      .map((snapshot) {
        Map? data = snapshot.data();
        if (data == null) return [];
        if (data.containsKey('roundDone')) {
          String done = data['roundDone'];
          if (data.containsKey(done)) {
            List<RankData> scores = [];
            Map<String, dynamic> scoreList = data[done];
            for (final s in scoreList.entries) {
              scores.add(RankData.fromMap(int.parse(s.key), s.value));
            }
            return scores;
          } else {
            return [];
          }
        } else {
          return [];
        }
  });
});

final seatingProvider = StreamProvider<List<RoundData>>((ref) async* {
  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection
      .doc('seating')
      .snapshots()
      .map((snapshot) {
        Map<String, dynamic> data = snapshot.data() ?? {};
        if (!data.containsKey('rounds')) {
          return <RoundData>[];
        }
        return [for
          (final Map oneRound in data['rounds'])
          RoundData.fromMap(oneRound.cast())];
  });
});

final gameProvider = StreamProvider<List<GameData>>((ref) async* {
  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection
      .doc('scores') //
      .snapshots()
      .map((snapshot) {
        Map<String, Map> data = (snapshot.data() ?? {}).cast();
        List<GameData> out = data.entries.map(GameData.fromMap).toList();
        return out;
  });
});

final scheduleProvider = StreamProvider<ScheduleData>((ref) async* {
  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection.doc('seating').snapshots().map((snapshot) {
    ScheduleData out = ScheduleData(timezone: UTC, rounds: const []);
    Map<String, dynamic> data = snapshot.data() ?? {};
    if (data.containsKey('timezone') && data.containsKey('rounds')) {
      out = ScheduleData.fromSeating(data);
    }
    return out;
  });
});

typedef RoundScore = ({
  String name,
  DateTime start, // TODO do we use this anywhere? What's the rationale for having this here?
  int score,
});

typedef PlayerScore = ({
  PlayerId id,
  String name,
  String rank,
  int total,
  int penalty,
  List<RoundScore> roundScores,
});

final playerScoreListProvider = StreamProvider((ref) async* {
  final rankings = await ref.watch(rankingProvider.future);
  final playerList = await ref.watch(playerListProvider.future);
  final games = await ref.watch(gameProvider.future);
  final schedule = await ref.watch(scheduleProvider.future);
  final playerNames =
      Map.fromEntries(playerList.map((e) => MapEntry(e.id, e.name)));

  yield [
    for (final ranking in rankings)
      (
        id: ranking.id,
        name: playerNames[ranking.id]!,
        rank: ranking.rank,
        total: ranking.total,
        penalty: ranking.penalty,
        roundScores: [for (final hanchan in games.withPlayerId(ranking.id))
          (
          name: schedule.rounds.firstWhere((rnd) => rnd.id == hanchan.roundId).name,
          score: hanchan.scores[hanchan.playerIndex(ranking.id)].finalScore,
          start: DateTime.now(),
          )
        ],
      )
  ];
});
