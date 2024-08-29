import 'package:alarm/alarm.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final alarmRingProvider = StreamProvider((ref) {
  return Alarm.ringStream.stream.map((alarmSettings) {
    if (alarmSettings.dateTime.isBefore(
            DateTime.now().subtract(const Duration(minutes: 30)))) {
      Alarm.stop(alarmSettings.id);
    } else {
      Future.delayed(const Duration(minutes: 30), () {
        Alarm.stop(alarmSettings.id);
      });
    }
    return alarmSettings;
  });
});
