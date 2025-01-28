import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timezone/timezone.dart';

import 'models.dart';
import 'providers/firestore.dart';
import 'providers/location.dart';
import 'providers/shared_preferences.dart';
import '/utils.dart';

export 'providers/fcm.dart';
export 'providers/firestore.dart';
export 'providers/location.dart';
export 'providers/shared_preferences.dart';
export 'providers/seat_map.dart';
export 'providers/filters.dart';

typedef AlarmInfo = ({
  RoundId id,
  String name,
  TZDateTime alarm,
  bool vibratePref,
  ({
    PlayerId id,
    String name,
    String table,
  })? player
});

final useWindsProvider = Provider<bool>((ref) {
  final tournament = ref.watch(tournamentProvider);
  return tournament.valueOrNull?.useWinds ?? false;
});

final alarmScheduleProvider = StreamProvider<List<AlarmInfo>>((ref) async* {
  final location = await ref.watch(locationProvider.future);
  final seating = await ref.watch(seatingProvider.future);
  final scheduleRounds = await ref.watch(scheduleProvider.future);
  final selectedPlayer = ref.watch(selectedPlayerProvider);
  final alarmsOn = ref.watch(alarmPrefProvider);
  final vibratePref = ref.watch(vibratePrefProvider);

  if (!alarmsOn) {
    yield [];
    return;
  }

  yield [
    for (final round in seating)
      if (scheduleRounds.rounds.any((rnd) => rnd.id == round.id))
        (
          id: round.id,
          vibratePref: vibratePref,
          name: scheduleRounds.rounds
              .firstWhere((rnd) => rnd.id == round.id)
              .name,
          alarm: TZDateTime.from(
            scheduleRounds.rounds
                .firstWhere((rnd) => rnd.id == round.id)
                .start,
            location,
          ).subtract(const Duration(minutes: 5)),
          player: selectedPlayer != null
              ? (
                  id: selectedPlayer.id,
                  name: selectedPlayer.name,
                  table: round.tableNameForSeat(selectedPlayer.seat),
                )
              : null,
        ),
  ];
});

extension SelectAsyncValue<State> on StreamProvider<State> {
  ProviderListenable<AsyncValue<Selected>> selectAsyncData<Selected>(
    Selected Function(State value) selector,
  ) {
    return select((e) => e.whenData(selector));
  }
}

void asyncDataListener<T>(
  void Function(T? previous, T next) listener,
  AsyncValue<T>? previous,
  AsyncValue<T> next,
) async {
  if (!next.hasValue) return;

  final previousValue = previous?.valueOrNull;
  final nextValue = next.value;
  if (identical(previousValue, nextValue)) return;

  if (nextValue case T nextValue) {
    return listener(previousValue, nextValue);
  }
}

extension WidgetRefListen on WidgetRef {
  void listenAsyncData<T>(
    ProviderListenable<AsyncValue<T>> provider,
    void Function(T? previous, T next) listener, {
    void Function(Object error, StackTrace stackTrace)? onError,
  }) =>
      listen(
        provider,
        (previous, next) => asyncDataListener(listener, previous, next),
        onError: onError,
      );
}

extension RefListen on Ref {
  ProviderSubscription<AsyncValue<T>> listenAsyncData<T>(
    ProviderListenable<AsyncValue<T>> provider,
    void Function(T? previous, T next) listener, {
    void Function(Object error, StackTrace stackTrace)? onError,
    bool fireImmediately = false,
  }) =>
      listen(
        provider,
        (previous, next) => asyncDataListener(listener, previous, next),
        onError: onError,
        fireImmediately: fireImmediately,
      );
}

extension AutoDisposeRefListen on Ref {
  ProviderSubscription<AsyncValue<T>> listenAsyncData<T>(
    ProviderListenable<AsyncValue<T>> provider,
    void Function(T? previous, T next) listener, {
    void Function(Object error, StackTrace stackTrace)? onError,
    bool fireImmediately = false,
  }) =>
      listen(
        provider,
        (previous, next) => asyncDataListener(listener, previous, next),
        onError: onError,
        fireImmediately: fireImmediately,
      );
}
