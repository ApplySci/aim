import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:collection/collection.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timezone/timezone.dart';

import '/models.dart';
import '/utils.dart';
import 'shared_preferences.dart';
import 'seat_map.dart';

final firebaseProvider = Provider((ref) => FirebaseFirestore.instance);

final allTournamentsListProvider = StreamProvider((ref) {
  final db = ref.watch(firebaseProvider);
  final snapshots = db.collection('tournaments').snapshots();

  return snapshots.map((query) => [
    for (final doc in query.docs)
      TournamentData.fromMap({
        'id': doc.id,
        'address': '',
        ...(doc.data() as Map).cast(),
      }),
  ]);
});

final tournamentListProvider = Provider.family<List<TournamentData>, WhenTournament>((ref, when) {
  final allTournaments = ref.watch(allTournamentsListProvider).value ?? [];
  final testMode = ref.watch(testModePrefProvider);

  return allTournaments.where((tournament) {
    return switch (when) {
      WhenTournament.all => true,
      WhenTournament.live => tournament.status == 'live',
      WhenTournament.upcoming => tournament.status == 'upcoming',
      WhenTournament.past => tournament.status == 'past',
      WhenTournament.test => testMode && tournament.status == 'test',
    };
  }).toList();
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

  return db.collection('tournaments').doc(tournamentId).collection('v3');
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

final allRankingsProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection.doc('ranking').snapshots().map((snapshot) {
    return snapshot.data() ?? {};
  });
});

final rankingProvider = StreamProvider<List<PlayerRankData>>((ref) async* {
  final allRankings = ref.watch(allRankingsProvider);

  yield* allRankings.when(
    data: (data) async* {
      if (data.containsKey('roundDone')) {
        String done = data['roundDone'];
        if (data.containsKey(done)) {
          List<PlayerRankData> scores = [];
          Map<String, dynamic> scoreList = data[done];
          for (final s in scoreList.entries) {
            scores.add(PlayerRankData.fromMap(int.parse(s.key), s.value));
          }
          scores.sort((a, b) => b.total.compareTo(a.total));
          yield scores;
        } else {
          yield [];
        }
      } else {
        yield [];
      }
    },
    loading: () => Stream.value([]),
    error: (_, __) => Stream.value([]),
  );
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
    List<GameData> out = [];
    for (int i = 1; i <= data.entries.length; i++) {
      final String key = i.toString();
      out.add(GameData.fromMap(key, data[key] as Map));
    }
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
  int seat,
  String name,
  int rank,
  bool tied,
  int total,
  int penalty,
  List<HanchanScore?> scores,  // Make individual scores nullable
});

final playerScoreListProvider = StreamProvider<List<PlayerScore>>((ref) async* {
  final rankings = await ref.watch(rankingProvider.future);
  final seatMap = await ref.watch(seatMapProvider.future);
  final games = await ref.watch(gameProvider.future);

  if (rankings.isEmpty || games.isEmpty || seatMap.length < 2) {
    yield [];
  } else {
    yield [
      for (final ranking in rankings)
        (
          id: seatMap[ranking.seat]?.id ?? 'unknown',
          seat: ranking.seat,
          name: seatMap[ranking.seat]!.name,
          rank: ranking.rank,
          tied: ranking.tied,
          total: ranking.total,
          penalty: ranking.penalty,
          scores: [
            for (final game in games)
              for (final table in game.tables)
                for (final scores in table.scores)
                  if (scores.seat == ranking.seat) scores,
          ],
        ),
    ];
  }
});

typedef PlayerRankings = ({
  List<int> rankings,
  List<int> totalScores,
  PlayerScore games,
});

final playerScoreProvider = StreamProvider.family
    .autoDispose<PlayerRankings, int>((ref, seat) async* {
  final playerScoreList = await ref.watch(playerScoreListProvider.future);
  final rankingList = await ref.watch(allRankingsProvider.future);

  final List<HanchanScore> emptyList = [];
  PlayerScore games = (
        id: 'unknown',
        seat: seat,
        name: '',
        rank: 0,
        tied: false,
        total: 0,
        penalty: 0,
        scores: emptyList,
      );
  if (seat >= 0 && playerScoreList.isNotEmpty) {
    try {
      games = playerScoreList.firstWhere((e) => e.seat == seat);
    } catch (e) {
      // pass
    }
  }

  List<int> rankings = [];
  List<int> totalScores = [];
  // extract from rankingList just the rankings and totals for this player
  if (rankingList.containsKey('roundDone')) {
    int endRound = int.parse(rankingList['roundDone']);
    for (int i = 1; i <= endRound; i++) {
      // Check if the round and seat exist in rankings before accessing
      if (rankingList.containsKey("$i") && 
          rankingList["$i"].containsKey("$seat") &&
          rankingList["$i"]["$seat"] != null) {
        rankings.add(rankingList["$i"]["$seat"]['r']);
        totalScores.add(rankingList["$i"]["$seat"]['total']);
      } else {
        // Add placeholder values for rounds where the substitute wasn't playing
        rankings.add(0);  // or whatever default rank makes sense
        totalScores.add(0);  // or whatever default score makes sense
      }
    }
  }

  PlayerRankings out = (
    games: games,
    rankings: rankings,
    totalScores: totalScores,
  );
  yield out;
});

final tournamentStatusProvider = Provider<WhenTournament>((ref) {
  final tournamentData = ref.watch(tournamentProvider).valueOrNull;
  if (tournamentData == null) return WhenTournament.upcoming;

  return switch (tournamentData.status) {
    'upcoming' => WhenTournament.upcoming,
    'live' => WhenTournament.live,
    'past' => WhenTournament.past,
    'test' => WhenTournament.test,
    _ => WhenTournament.upcoming,
  };
});
