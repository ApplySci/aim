import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:collection/collection.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timezone/timezone.dart';

import '/models.dart';
import 'shared_preferences.dart';

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
          TournamentData.fromMap({
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
      .map((snapshot) => TournamentData.fromMap({
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
      return [
        for (final Map<String, dynamic> player in data['players'])
          PlayerData(player.cast())
      ];
    } else {
      return [];
    }
  });
});

final playerMapProvider = StreamProvider((ref) async* {
  final playerList = await ref.watch(playerListProvider.future);
  yield {
    for (final player in playerList) player.id: player,
  };
});

final selectedPlayerProvider = Provider((ref) {
  final selectedPlayerId = ref.watch(selectedPlayerIdProvider);
  if (selectedPlayerId == null) return null;

  final playerList = ref.watch(playerListProvider).valueOrNull;
  return playerList
      ?.firstWhereOrNull((player) => player.id == selectedPlayerId);
});

final rankingProvider = StreamProvider<List<PlayerRankData>>((ref) async* {
  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection.doc('ranking').snapshots().map((snapshot) {
    Map? data = snapshot.data();
    if (data == null) return [];
    if (data.containsKey('roundDone')) {
      String done = data['roundDone'];
      if (data.containsKey(done)) {
        List<PlayerRankData> scores = [];
        Map<String, dynamic> scoreList = data[done];
        for (final s in scoreList.entries) {
          scores.add(PlayerRankData.fromMap(int.parse(s.key), s.value));
        }
        scores.sort((a, b) => b.total.compareTo(a.total));
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

  yield* collection.doc('seating').snapshots().map((snapshot) {
    Map<String, dynamic> data = snapshot.data() ?? {};
    if (!data.containsKey('rounds')) {
      return [];
    }
    return [
      for (final Map round in data['rounds']) RoundData.fromMap(round.cast()),
    ];
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
    final data = snapshot.data() ?? {};
    if (data.containsKey('timezone') && data.containsKey('rounds')) {
      out = ScheduleData.fromSeating(data);
    }
    return out;
  });
});

final roundListProvider = StreamProvider((ref) async* {
  final schedule = await ref.watch(scheduleProvider.future);
  yield schedule.rounds;
});

final roundMapProvider = StreamProvider((ref) async* {
  final roundList = await ref.watch(roundListProvider.future);
  yield {
    for (final round in roundList) round.id: round,
  };
});

typedef PlayerScore = ({
  PlayerId id,
  String name,
  int rank,
  bool tied,
  int total,
  int penalty,
  List<HanchanScore> scores,
});

final playerScoreListProvider = StreamProvider<List<PlayerScore>>((ref) async* {
  final rankings = await ref.watch(rankingProvider.future);
  final playerMap = await ref.watch(playerMapProvider.future);
  final games = await ref.watch(gameProvider.future);

  yield [
    for (final ranking in rankings)
      (
        id: ranking.id,
        name: playerMap[ranking.id]!.name,
        rank: ranking.rank,
        tied: ranking.tied,
        total: ranking.total,
        penalty: ranking.penalty,
        scores: [
          for (final game in games)
            for (final table in game.tables)
              for (final scores in table.scores)
                if (scores.playerId == ranking.id) scores,
        ],
      ),
  ];
});
