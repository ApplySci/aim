import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

final sharedPreferencesProvider = Provider<SharedPreferences>(
  (ref) => throw UnimplementedError(),
);

extension Let<T> on T {
  R let<R>(R Function(T) block) => block(this);
}

mixin SharedPreferencesValueMixin<T> {
  SharedPreferences get _prefs;
  String get _key;

  T? _getValue();

  Future<void> _setValue(T value);

  Future<void> set(T? value) async {
    if (value != null) {
      await _setValue(value);
    } else {
      await _prefs.remove(_key);
    }
  }
}

abstract class SharedPreferencesValueNNotifier<T> extends Notifier<T?>
    with SharedPreferencesValueMixin<T> {
  SharedPreferencesValueNNotifier({
    required String key,
  }) : _key = key;

  @override
  late SharedPreferences _prefs;
  @override
  final String _key;

  @override
  T? build() {
    _prefs = ref.watch(sharedPreferencesProvider);
    return _getValue();
  }

  T? get get => state;

  @override
  Future<void> set(T? value) async {
    await super.set(value);
    state = value;
  }
}

abstract class SharedPreferencesValueNotifier<T> extends Notifier<T>
    with SharedPreferencesValueMixin<T> {
  SharedPreferencesValueNotifier({
    required String key,
    required T fallback,
  })  : _key = key,
        _fallback = fallback;

  @override
  late SharedPreferences _prefs;
  @override
  final String _key;
  final T _fallback;

  @override
  T build() {
    _prefs = ref.watch(sharedPreferencesProvider);
    return _getValue() ?? _fallback;
  }

  T get get => state;

  @override
  Future<void> set(T? value) async {
    await super.set(value);
    state = value ?? _fallback;
  }
}

mixin SharedPreferencesStringMixin
    implements SharedPreferencesValueMixin<String> {
  @override
  String? _getValue() => _prefs.getString(_key);

  @override
  Future<void> _setValue(String value) => _prefs.setString(_key, value);
}

class SharedPreferencesStringNNotifier
    extends SharedPreferencesValueNNotifier<String>
    with SharedPreferencesStringMixin {
  SharedPreferencesStringNNotifier({
    required super.key,
  });
}

class SharedPreferencesStringNotifier
    extends SharedPreferencesValueNotifier<String>
    with SharedPreferencesStringMixin {
  SharedPreferencesStringNotifier({
    required super.key,
    required super.fallback,
  });
}

mixin SharedPreferencesBoolMixin implements SharedPreferencesValueMixin<bool> {
  @override
  bool? _getValue() => _prefs.getBool(_key);

  @override
  Future<void> _setValue(bool value) => _prefs.setBool(_key, value);
}

class SharedPreferencesBoolNNotifier
    extends SharedPreferencesValueNNotifier<bool>
    with SharedPreferencesBoolMixin {
  SharedPreferencesBoolNNotifier({
    required super.key,
  });
}

class SharedPreferencesBoolNotifier
    extends SharedPreferencesValueNotifier<bool>
    with SharedPreferencesBoolMixin {
  SharedPreferencesBoolNotifier({
    required super.key,
    required super.fallback,
  });
}

final alarmPrefProvider = NotifierProvider<SharedPreferencesBoolNotifier, bool>(
  () => SharedPreferencesBoolNotifier(key: 'alarm', fallback: kReleaseMode || false),
);

final scorePrefProvider = NotifierProvider<SharedPreferencesBoolNotifier, bool>(
  () => SharedPreferencesBoolNotifier(key: 'score', fallback: true),
);

final seatingPrefProvider =
    NotifierProvider<SharedPreferencesBoolNotifier, bool>(
  () => SharedPreferencesBoolNotifier(key: 'seating', fallback: true),
);

final timezonePrefProvider =
    NotifierProvider<SharedPreferencesBoolNotifier, bool>(
  () => SharedPreferencesBoolNotifier(key: 'tz', fallback: true),
);

final tournamentIdProvider = NotifierProvider<TournamentIdNotifier, String?>(
  () => TournamentIdNotifier(),
);

class TournamentIdNotifier extends Notifier<String?> {
  late SharedPreferences _prefs;

  @override
  String? build() {
    _prefs = ref.watch(sharedPreferencesProvider);
    return _getValue();
  }

  String get _key => 'tournamentId';

  String? _getValue() => _prefs.getString(_key);

  Future<void> set(String? value) async {
    if (value != null) {
      await _prefs.setString(_key, value);
    } else {
      await _prefs.remove(_key);
    }
    state = value;
  }
}

final selectedPlayerIdProvider = NotifierProvider<SelectedPlayerIdNotifier, int?>(
  () => SelectedPlayerIdNotifier(),
);

class SelectedPlayerIdNotifier extends Notifier<int?> {
  late SharedPreferences _prefs;

  @override
  int? build() {
    _prefs = ref.watch(sharedPreferencesProvider);
    final tournamentId = ref.watch(tournamentIdProvider);
    return _getValueForTournament(tournamentId);
  }

  String get _key => 'selectedPlayer';

  int? _getValueForTournament(String? tournamentId) {
    if (tournamentId == null) return null;
    final String? jsonString = _prefs.getString(_key);
    if (jsonString == null) return null;
    final Map<String, dynamic> selectedPlayers = 
        (jsonDecode(jsonString) as Map<String, dynamic>?) ?? {};
    return selectedPlayers[tournamentId] as int?;
  }

  Future<void> set(int? value) async {
    final tournamentId = ref.read(tournamentIdProvider);
    if (tournamentId == null) return;
    if (value != null) {
      await _setValue(value);
    } else {
      final String? jsonString = _prefs.getString(_key);
      final Map<String, dynamic> selectedPlayers = 
          (jsonDecode(jsonString ?? '{}') as Map<String, dynamic>?) ?? {};
      selectedPlayers.remove(tournamentId);
      await _prefs.setString(_key, jsonEncode(selectedPlayers));
    }
    state = value;
  }

  Future<void> _setValue(int value) async {
    final tournamentId = ref.read(tournamentIdProvider);
    if (tournamentId == null) return;
    final String? jsonString = _prefs.getString(_key);
    final Map<String, dynamic> selectedPlayers = 
        (jsonDecode(jsonString ?? '{}') as Map<String, dynamic>?) ?? {};
    selectedPlayers[tournamentId] = value;
    await _prefs.setString(_key, jsonEncode(selectedPlayers));
  }
}

final japaneseNumbersProvider =
    NotifierProvider<SharedPreferencesBoolNotifier, bool>(
  () => SharedPreferencesBoolNotifier(key: 'japaneseNumbers', fallback: false),
);

final japaneseWindsProvider =
    NotifierProvider<SharedPreferencesBoolNotifier, bool>(
  () => SharedPreferencesBoolNotifier(key: 'japaneseWinds', fallback: false),
);

final negSignProvider = Provider((ref) {
  final japaneseNumbers = ref.watch(japaneseNumbersProvider);
  return japaneseNumbers ? '▲' : '-';
});

final tournamentPlayerIdProvider = Provider((ref) {
  final tournamentId = ref.watch(tournamentIdProvider);
  final playerId = ref.watch(selectedPlayerIdProvider);
  return (
    tournamentId: tournamentId,
    playerId: playerId,
  );
});

final vibratePrefProvider = NotifierProvider<SharedPreferencesBoolNotifier, bool>(
  () => SharedPreferencesBoolNotifier(key: 'vibrate', fallback: true),
);