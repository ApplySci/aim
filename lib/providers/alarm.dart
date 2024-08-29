import 'package:alarm/alarm.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final alarmRingProvider = StreamProvider((ref) {
  return Alarm.ringStream.stream.map((alarmSettings) {
    // Start a timer when the alarm starts ringing. stop the alarm after 30 minutes.
    Future.delayed(const Duration(minutes: 30), () {
      Alarm.stop(alarmSettings.id);
    });
    return alarmSettings;
  });
});
