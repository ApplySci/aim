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
  });

  factory TournamentData.fromJson(Map<String, dynamic> data) => TournamentData(
        id: data['id'] as TournamentId,
        name: data['name'] as String,
        address: data['address'] as String,
        country: data['country'] as String,
        startDate: data['start_date'] as Timestamp,
        endDate: data['end_date'] as Timestamp,
        status: data['status'] as String,
        rules: data['rules'] as String,
      );

  final TournamentId id;
  final String name;
  final String address;
  final String country;
  final Timestamp startDate;
  final Timestamp endDate;
  final String status;
  final String rules;

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
      ];
}

typedef PlayerId = int;

class PlayerData extends Equatable implements Comparable<PlayerData> {
  const PlayerData(this.id, this.name);

  final PlayerId id;
  final String name;

  @override
  int compareTo(PlayerData other) => name.compareTo(other.name);

  @override
  List<Object?> get props => [
        id,
        name,
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

class ScheduleData extends Equatable {
  const ScheduleData({
    required this.timezone,
    required this.rounds,
  });

  factory ScheduleData.fromJson(Map<String, dynamic> data) {
    final location = getLocation(data.remove('timezone') as String);
    final roundScheduleList = data.entries.map((e) => {
          'id': e.key,
          ...e.value,
        });
    return ScheduleData(
      timezone: location,
      rounds: [
        for (final roundSchedule in roundScheduleList)
          RoundScheduleData.fromJson(
            roundSchedule.cast(),
            location,
          ),
      ],
    );
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

  factory RoundScheduleData.fromJson(
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
  final DateTime start;

  @override
  List<Object?> get props => [
        name,
        start,
      ];
}

class ScoreData extends Equatable {
  const ScoreData({
    required this.id,
    required this.rank,
    required this.total,
    required this.penalty,
    required this.roundScores,
    required this.roundDone,
  });

  factory ScoreData.fromJson(Map<String, dynamic> data) => ScoreData(
        id: data['id'] as int,
        rank: data['r'] as String,
        total: data['t'] as int,
        penalty: data['p'] as int,
        roundScores: (data['s'] as List).cast(),
        roundDone: (data['roundDone'] as int?) ?? 0,
      );

  final PlayerId id;
  final String rank;
  final int total;
  final int penalty;
  final List<int> roundScores;
  final int roundDone;

  @override
  List<Object?> get props => [
        id,
        rank,
        total,
        penalty,
        roundScores,
        roundDone,
      ];
}

extension RoundDataList on List<RoundData> {
  Iterable<RoundData> withPlayerId(PlayerId? playerId) => playerId == null
      ? this
      : map((round) => RoundData(
            id: round.id,
            tables: {
              for (final MapEntry(:key, :value) in round.tables.entries)
                if (value.contains(playerId)) key: value,
            },
          ));
}

class RoundData extends Equatable {
  const RoundData({
    required this.id,
    required this.tables,
  });

  factory RoundData.fromJson(Map<String, dynamic> data) => RoundData(
        id: data['id'] as String,
        tables: (data['tables'] as Map).map(
          (key, value) => MapEntry(
            key as String,
            (value as List).cast(),
          ),
        ),
      );

  final String id;
  final Map<String, List<PlayerId>> tables;

  String tableNameForPlayerId(PlayerId playerId) =>
      tables.entries.firstWhere((e) => e.value.contains(playerId)).key;

  @override
  List<Object?> get props => [
        id,
        tables,
      ];
}
