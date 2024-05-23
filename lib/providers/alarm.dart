import 'package:alarm/alarm.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final alarmRingProvider = StreamProvider((ref) => Alarm.ringStream.stream);
