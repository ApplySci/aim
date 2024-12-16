import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:collection/collection.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timezone/timezone.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

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
      if (doc.exists && doc.data().isNotEmpty)
        TournamentData.fromMap({
          'id': doc.id,
          'address': '',
          'name': '',
          'country': '',
          'status': 'upcoming',
          ...doc.data(),
        })
  ]);
});

final tournamentListProvider = Provider.family<List<TournamentData>, WhenTournament>((ref, when) {
  if (when == WhenTournament.past) {
    final summaries = ref.watch(pastTournamentSummariesProvider).value ?? [];
    return [
      for (final summary in summaries)
        TournamentData.fromMap({
          'id': summary.id,
          'name': summary.name,
          'address': summary.venue,
          'country': summary.country,
          'start_date': summary.startDate,
          'end_date': summary.endDate,
          'status': 'past',
          'rules': summary.rules,
        })
    ];
  }

  final allTournaments = ref.watch(allTournamentsListProvider).value ?? [];
  final testMode = ref.watch(testModePrefProvider);

  return allTournaments.where((tournament) {
    return switch (when) {
      WhenTournament.all => true,
      WhenTournament.live => tournament.status == 'live',
      WhenTournament.upcoming => tournament.status == 'upcoming',
      WhenTournament.test => testMode && tournament.status == 'test',
      WhenTournament.past => false,
    };
  }).toList();
});

final tournamentProvider = StreamProvider<TournamentData>((ref) async* {
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return;

  final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;
  if (tournamentStatus == WhenTournament.past) {
    yield await ref.watch(pastTournamentDetailsProvider(tournamentId).future);
    return;
  }

  final db = ref.watch(firebaseProvider);
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
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return;

  final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;
  if (tournamentStatus == WhenTournament.past) {
    final tournament = await ref.watch(pastTournamentDetailsProvider(tournamentId).future);
    yield tournament.players ?? [];
    return;
  }

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
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return;

  final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;
  if (tournamentStatus == WhenTournament.past) {
    final tournament = await ref.watch(pastTournamentDetailsProvider(tournamentId).future);
    if (tournament.rankings != null) {
      final roundDone = tournament.rankings!['roundDone'];
      if (roundDone != null) {
        final roundScores = tournament.rankings![roundDone.toString()];
        if (roundScores != null) {
          yield [
            for (final MapEntry(:key, :value) in (roundScores as Map<String, dynamic>).entries)
              PlayerRankData(
                seat: int.parse(key),
                rank: value['r'] as int,
                tied: value['t'] == 1,
                total: value['total'] as int,
                penalty: value['p'] as int,
              )
          ];
          return;
        }
      }
    }
    yield [];
    return;
  }

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
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return;

  final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;
  if (tournamentStatus == WhenTournament.past) {
    final tournament = await ref.watch(pastTournamentDetailsProvider(tournamentId).future);
    yield tournament.seating ?? [];
    return;
  }

  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection.doc('seating').snapshots().map((snapshot) {
    Map<String, dynamic> data = snapshot.data() ?? {};
    if (!data.containsKey('rounds')) {
      return [];
    }
    
    final location = getLocation(data['timezone'].toString());
    return [
      for (final Map round in data['rounds']) 
        RoundData.fromMap(round.cast(), location),
    ];
  });
});

final gameProvider = StreamProvider<List<GameData>>((ref) async* {
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return;

  final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;
  if (tournamentStatus == WhenTournament.past) {
    final tournament = await ref.watch(pastTournamentDetailsProvider(tournamentId).future);
    yield tournament.games ?? [];
    return;
  }

  final collection = ref.watch(tournamentCollectionProvider);
  if (collection == null) return;

  yield* collection
      .doc('scores')
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
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) return;

  final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;
  if (tournamentStatus == WhenTournament.past) {
    final tournament = await ref.watch(pastTournamentDetailsProvider(tournamentId).future);
    yield {
      for (final round in tournament.seating ?? [])
        round.id: RoundScheduleData(
          id: round.id,
          name: round.id,
          start: round.start,
        ),
    };
    return;
  }

  final schedule = await ref.watch(scheduleProvider.future);
  yield {
    for (final round in schedule.rounds) round.id: round,
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
  final tournamentId = ref.watch(tournamentIdProvider);
  final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;

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

  if (tournamentStatus == WhenTournament.past) {
    final tournament = await ref.watch(pastTournamentDetailsProvider(tournamentId!).future);
    if (tournament.rankings != null) {
      final maxRound = int.parse(tournament.rankings!['roundDone'].toString());
      for (int i = 1; i <= maxRound; i++) {
        final roundData = tournament.rankings![i.toString()];
        if (roundData != null && roundData[seat.toString()] != null) {
          rankings.add(roundData[seat.toString()]['r']);
          totalScores.add(roundData[seat.toString()]['total']);
        }
      }
    }
  } else {
    final rankingList = await ref.watch(allRankingsProvider.future);
    if (rankingList.containsKey('roundDone')) {
      int endRound = int.parse(rankingList['roundDone']);
      for (int i = 1; i <= endRound; i++) {
        if (rankingList.containsKey("$i") &&
            rankingList["$i"].containsKey("$seat") &&
            rankingList["$i"]["$seat"] != null) {
          rankings.add(rankingList["$i"]["$seat"]['r']);
          totalScores.add(rankingList["$i"]["$seat"]['total']);
        } else {
          rankings.add(0);
          totalScores.add(0);
        }
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

final tournamentStatusProvider = StreamProvider<WhenTournament>((ref) async* {
  final tournamentId = ref.watch(tournamentIdProvider);
  if (tournamentId == null) {
    yield WhenTournament.upcoming;
    return;
  }

  // Check if it's in the past tournaments list
  final pastSummaries = ref.watch(pastTournamentSummariesProvider).valueOrNull ?? [];
  if (pastSummaries.any((summary) => summary.id == tournamentId)) {
    yield WhenTournament.past;
    return;
  }

  // Otherwise check Firebase status
  final db = ref.watch(firebaseProvider);
  yield* db.collection('tournaments').doc(tournamentId).snapshots().map((snapshot) {
    final status = snapshot.data()?['status'] as String? ?? 'upcoming';
    return switch (status) {
      'upcoming' => WhenTournament.upcoming,
      'live' => WhenTournament.live,
      'test' => WhenTournament.test,
      _ => WhenTournament.upcoming,
    };
  });
});

final pastTournamentsLastUpdatedProvider = StreamProvider<DateTime?>((ref) async* {
  final db = ref.watch(firebaseProvider);
  final doc = await db.collection('metadata').doc('past_tournaments').get();

  if (!doc.exists) {
    yield null;
    return;
  }

  yield* db
      .collection('metadata')
      .doc('past_tournaments')
      .snapshots()
      .map((snapshot) {
        final lastUpdated = snapshot.data()?['last_updated'];
        if (lastUpdated is Timestamp) {
          return lastUpdated.toDate();
        } else if (lastUpdated is String) {
          return DateTime.parse(lastUpdated);
        }
        return null;
      });
});

final pastTournamentsMetadataProvider = StreamProvider<Map<String, dynamic>?>((ref) async* {
  final db = ref.watch(firebaseProvider);
  yield* db
      .collection('metadata')
      .doc('past_tournaments')
      .snapshots()
      .map((snapshot) => snapshot.data());
});

final pastTournamentSummariesProvider = FutureProvider<List<PastTournamentSummary>>((ref) async {
  final metadata = await ref.watch(pastTournamentsMetadataProvider.future);

  if (metadata == null) {
    Log.warn('No past tournaments metadata found');
    return [];
  }

  try {
    final response = await http.get(Uri.parse('${metadata["api_base_url"]}/static/data/past_tournaments.json'));

    if (response.statusCode != 200) {
      Log.warn('API error: ${response.body}');
      return [];
    }

    final data = jsonDecode(response.body);
    return List<PastTournamentSummary>.from(
      data['tournaments'].map((item) => PastTournamentSummary.fromMap(item))
    );
  } catch (e, stackTrace) {
    Log.error('Error fetching past tournaments: $e\n$stackTrace');
    return [];
  }
});

final pastTournamentDetailsProvider = FutureProvider.family<TournamentData, String>((ref, tournamentId) async {
  final metadata = await ref.watch(pastTournamentsMetadataProvider.future);
  final baseUrl = metadata?['api_base_url'] as String?;

  if (baseUrl == null || baseUrl.isEmpty) {
    Log.error('No API base URL configured in past_tournaments metadata');
    throw Exception('No API base URL configured');
  }

  final url = '$baseUrl/api/tournament/$tournamentId';
  final response = await http.get(Uri.parse(url));

  if (response.statusCode != 200) {
    Log.warn('Failed to load tournament details: ${response.body}');
    throw Exception('Failed to load tournament details');
  }

  Map data = jsonDecode(response.body);
  return TournamentData.fromMap({'id': tournamentId, ...data});
});
