import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:equatable/equatable.dart';
import 'package:timezone/timezone.dart';

import 'utils.dart';

enum Wind {
  east('E', '東'),
  south('S', '西'),
  west('W', '南'),
  north('N', '北');

  const Wind(this.western, this.japanese);

  final String japanese;
  final String western;
}

typedef TournamentId = String;

class TournamentData extends Equatable {
  const TournamentData({
    required this.id,
    required this.name,
    required this.address,
    required this.country,
    required this.startDate,
    required this.endDate,
    required this.status,
    required this.rules,
    required this.htmlnotes,
    this.url,
    this.urlIcon,
    this.players,
    this.seating,
    this.games,
    this.rankings,
    this.useWinds = false,
  });

  factory TournamentData.fromMap(Map<String, dynamic> data) {
    // For past tournaments, we might get a null status
    final status = data['status'] as String? ?? 'past';

    // Handle both Timestamp and String/DateTime date formats
    final startDate = data['start_date'] is Timestamp
        ? data['start_date'] as Timestamp
        : Timestamp.fromDate(
            data['start_date'] is DateTime
                ? data['start_date'] as DateTime
                : DateTime.parse(data['start_date'] as String)
          );

    final endDate = data['end_date'] is Timestamp
        ? data['end_date'] as Timestamp
        : Timestamp.fromDate(
            data['end_date'] is DateTime
                ? data['end_date'] as DateTime
                : DateTime.parse(data['end_date'] as String)
          );

    // Handle players data
    List<PlayerData>? players;
    if (data.containsKey('players') && data['players'] != null) {
        players = ((data['players'] as Map)['players'] as List).map((p) =>
          PlayerData(p as Map<String, dynamic>)
        ).toList();
    }

    // Handle seating data
    List<RoundData>? seating;
    if (data['seating'] != null && data['seating'] is Map && data['seating']['rounds'] is List) {
      final location = getLocation(data['seating']['timezone']);
      seating = (data['seating']['rounds'] as List).map((s) =>
        RoundData.fromMap(s as Map<String, dynamic>, location)
      ).toList();
    }

    // Handle games data
    List<GameData>? games;
    if (data.containsKey('scores') && data['scores'] is Map) {
      games = data['scores'].entries.map<GameData>((e) =>
        GameData.fromMap(e.key, e.value as Map<String, dynamic>)
      ).toList();
    }

    // Handle rankings data
    Map<String, dynamic>? rankings;
    if (data.containsKey('ranking') && data['ranking'] is Map) {
      final rawRankings = data['ranking'] as Map;
      rankings = {
        'roundDone': rawRankings['roundDone']?.toString() ?? '0',
        for (final MapEntry(:key, :value) in rawRankings.entries)
          if (key != 'roundDone')
            key.toString(): {
              for (final MapEntry(key: seatKey, value: seatValue) in (value as Map).entries)
                seatKey.toString(): {
                  'r': seatValue['r'] as int,
                  't': seatValue['t'] as int,
                  'p': seatValue['p'] as int,
                  'total': seatValue['total'] as int,
                },
            },
      };
    }

    return TournamentData(
      id: data['id'] as String,
      name: data['name'] as String,
      address: data['address'] as String? ?? '',
      country: data['country'] as String? ?? '',
      startDate: startDate,
      endDate: endDate,
      status: status,
      rules: data['rules'] as String? ?? '',
      htmlnotes: data['htmlnotes'] as String? ?? '',
      url: data['url'] as String?,
      urlIcon: data['url_icon'] as String?,
      players: players,
      seating: seating,
      games: games,
      rankings: rankings,
      useWinds: data['use_winds'] ?? false,
    );
  }

  final TournamentId id;
  final String name;
  final String address;
  final String country;
  final String? htmlnotes;
  final Timestamp startDate;
  final Timestamp endDate;
  final String status;
  final String rules;
  final String? url;
  final String? urlIcon;
  final List<PlayerData>? players;
  final List<RoundData>? seating;
  final List<GameData>? games;
  final Map<String, dynamic>? rankings;
  final bool useWinds;

  String get when => dateRange(startDate, endDate);

  @override
  List<Object?> get props => [
        id,
        name,
        address,
        country,
        startDate,
        endDate,
        status,
        rules,
        url,
        urlIcon,
        players,
        seating,
        games,
        rankings,
        useWinds,
      ];
}

typedef PlayerId = String;

class PlayerData extends Equatable implements Comparable<PlayerData> {
  final PlayerId id;
  final int seat;
  final String name;

  PlayerData(Map<String, dynamic> playerMap)
      : id = playerMap['registration_id'],
        seat = playerMap['seating_id'] ?? -1,
        name = playerMap['name'];

  @override
  int compareTo(PlayerData other) => id.compareTo(other.id);

  @override
  List<Object?> get props => [
        id,
        name,
        seat,
      ];
}

extension PlayerList on List<PlayerData> {
  PlayerData? byId(PlayerId id) {
    try {
      return firstWhere((player) => player.id == id);
    } on StateError {
      return null;
    }
  }
}

typedef RoundId = String;
typedef TableId = String;

class ScheduleData extends Equatable {
  const ScheduleData({
    required this.timezone,
    required this.rounds,
  });

  factory ScheduleData.fromSeating(Map<String, dynamic> data) {
    final location = getLocation(data['timezone'].toString());

    List<RoundScheduleData> rounds = [];
    for (final Map<String, dynamic> roundSchedule in data['rounds']) {
      RoundScheduleData newRound = RoundScheduleData.fromMap(
        roundSchedule,
        location,
      );
      rounds.add(newRound);
    }

    return ScheduleData(timezone: location, rounds: rounds);
  }

  final Location timezone;
  final List<RoundScheduleData> rounds;

  @override
  List<Object?> get props => [
        timezone,
        rounds,
      ];
}

class RoundScheduleData extends Equatable {
  const RoundScheduleData({
    required this.id,
    required this.name,
    required this.start,
  });

  factory RoundScheduleData.fromMap(
    Map<String, dynamic> data,
    Location location,
  ) =>
      RoundScheduleData(
        id: data['id'] as RoundId,
        name: data['name'] as String,
        start: TZDateTime.from(
          DateTime.parse(data['start'] as String),
          location,
        ),
      );

  final RoundId id;
  final String name;
  final TZDateTime start;

  @override
  List<Object?> get props => [
        name,
        start,
      ];
}

class PlayerRankData extends Equatable {
  // one player's score
  const PlayerRankData({
    required this.seat,
    required this.rank,
    required this.tied,
    required this.total,
    required this.penalty,
  });

  factory PlayerRankData.fromMap(int seat, Map<String, dynamic> data) =>
      PlayerRankData(
        seat: seat,
        rank: data['r'] as int,
        tied: data['t'] == 1,
        total: data['total'] as int,
        penalty: data['p'] as int,
      );

  final int seat;
  final int rank;
  final bool tied;
  final int total;
  final int penalty;

  @override
  List<Object?> get props => [
        seat,
        rank,
        tied,
        total,
        penalty,
      ];
}

extension RoundDataList on List<RoundData> {
  // seating
  Iterable<RoundData> withSeat(int? seat) => seat == null
      ? this
      : map((round) => RoundData(
            id: round.id,
            tables: [
              for (final table in round.tables)
                if (table.seats.contains(seat)) table,
            ],
          ));
}

class RoundData extends Equatable {
  // seating
  const RoundData({
    required this.id,
    required this.tables,
    this.name,
    this.start,
  });

  factory RoundData.fromMap(Map<String, dynamic> data, [Location? location]) => RoundData(
        id: data['id'] as String,
        name: data.containsKey('name') ? data['name'] : null,
        start: data.containsKey('start') ? TZDateTime.from(DateTime.parse(data['start'] as String), location!) : null,
        tables: data.containsKey('tables') ? [
          for (final MapEntry(:key, :value) in (data['tables'] as Map).entries)
            TableData(
              name: key,
              seats: (value as List).cast(),
            ),
        ] : [],
      );


  final String id;
  final List<TableData> tables;
  final String? name;
  final TZDateTime? start;

  String tableNameForSeat(int seat) =>
      tables.firstWhere((e) => e.seats.contains(seat)).name;

  @override
  List<Object?> get props => [
        id,
        tables,
      ];
}

class TableData extends Equatable {
  const TableData({
    required this.name,
    required this.seats,
  });

  final String name;
  final List<int> seats;

  @override
  List<Object?> get props => [
        name,
        seats,
      ];
}

extension HanchanList on List<GameData> {
  // List of detailed results for a given player
  List<Hanchan> withSeat(int seat) {
    // get one game for each round for the given player
    return [
      for (final hanchan in this)
        for (final table in hanchan.tables)
          if (table.hasSeat(seat)) table,
    ];
  }
}

class HanchanScore extends Equatable {
  // detailed score for one player at one table in one round
  final int seat;
  final int? placement;
  final int? gameScore;
  final int? finalScore;
  final int? penalties;

  const HanchanScore({
    required this.seat,
    this.placement,
    this.gameScore,
    this.finalScore,
    this.penalties,
  });

  factory HanchanScore.fromList(List<dynamic> values) {
    return HanchanScore(
      seat: values[0] as int,
      penalties: values[1] != null ? values[1] as int : null,
      gameScore: values[2] != null ? values[2] as int : null,
      placement: values[3] != null ? values[3] as int : null,
      finalScore: values[4] != null ? values[4] as int : null,
    );
  }

  int? get uma => finalScore != null && gameScore != null && penalties != null
      ? finalScore! - gameScore! - penalties!
      : null;

  @override
  List<Object?> get props => [
        seat,
        penalties,
        gameScore,
        placement,
        finalScore,
      ];
}

class Hanchan extends Equatable {
  // the scores for all four players at one table in one round
  final RoundId roundId;
  final TableId tableId;
  final List<HanchanScore> scores; // length 4: one HanchanScore for each player

  const Hanchan({
    required this.roundId,
    required this.tableId,
    required this.scores,
  });

  bool hasSeat(int seat) =>
      scores.any((e) => e.seat == seat);

  @override
  List<Object?> get props => [
        roundId,
        tableId,
        scores,
      ];
}

class GameData extends Equatable {
  const GameData({
    required this.roundId,
    required this.tables,
  });

  final RoundId roundId;
  final List<Hanchan> tables;

  factory GameData.fromMap(key, Map value) {
    final roundId = key as RoundId;
    final tables = value.entries.where((e) => e.key != 'missing').map((e) {
      final tableId = e.key as TableId;
      final tableData = e.value as Map;
      return Hanchan(
        roundId: roundId,
        tableId: tableId,
        scores: [
          for (final wind in Wind.values)
            if (tableData['${wind.index}'] != null)
              HanchanScore.fromList(
                (tableData['${wind.index}'] as List).cast<dynamic>()
              )
            else
              HanchanScore(seat: -1)  // or handle null case appropriately
        ],
      );
    }).toList();

    return GameData(
      roundId: roundId,
      tables: tables,
    );
  }

  @override
  List<Object?> get props => [
        roundId,
        tables,
      ];
}

class PastTournamentSummary extends Equatable {
  const PastTournamentSummary({
    required this.id,
    required this.name,
    required this.startDate,
    required this.endDate,
    required this.venue,
    required this.country,
    required this.rules,
    required this.playerCount,
  });

  final String id;
  final String name;
  final DateTime startDate;
  final DateTime endDate;
  final String venue;
  final String country;
  final String rules;
  final int playerCount;

  factory PastTournamentSummary.fromMap(Map<String, dynamic> data) => PastTournamentSummary(
    id: data['id'] as String,
    name: data['name'] as String,
    startDate: data['start_date'] is Timestamp
        ? (data['start_date'] as Timestamp).toDate()
        : DateTime.parse(data['start_date'] as String),
    endDate: data['end_date'] is Timestamp
        ? (data['end_date'] as Timestamp).toDate()
        : DateTime.parse(data['end_date'] as String),
    venue: data['venue'] as String,
    country: data['country'] as String,
    rules: data['rules'] as String,
    playerCount: data['player_count'] as int,
  );

  @override
  List<Object?> get props => [id, name, startDate, endDate, venue, country, rules, playerCount];
}
