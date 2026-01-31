import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/timezone.dart';

import 'firestore.dart';
import '/providers/shared_preferences.dart';

final timezoneProvider = FutureProvider<String>((ref) async {
  final info = await FlutterTimezone.getLocalTimezone();
  return info.identifier;
});

final localLocationProvider = FutureProvider((ref) async {
  return getLocation(await ref.watch(timezoneProvider.future));
});

final tournamentLocationProvider = StreamProvider((ref) async* {
  yield await ref.watch(scheduleProvider.selectAsync((e) => e.timezone));
});

final locationProvider = StreamProvider((ref) async* {
  final useEventTimezone = ref.watch(timezonePrefProvider);
  final localLocation = await ref.watch(localLocationProvider.future);
  final tournamentLocation = await ref.watch(tournamentLocationProvider.future);

  yield useEventTimezone ? localLocation : tournamentLocation;
});
