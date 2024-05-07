import 'package:alarm/model/alarm_settings.dart';
import 'package:alarm/alarm.dart';
import 'package:flutter/material.dart';

class AlarmScreen extends StatefulWidget {
  const AlarmScreen({super.key, required this.settings});

  final AlarmSettings settings;

  @override
  State<AlarmScreen> createState() => _AlarmScreenState();
}

class _AlarmScreenState extends State<AlarmScreen> {
  Future<void> stopAlarm() async {
    Alarm.stop(widget.settings.id).then((_) => Navigator.pop(context));
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: InkWell(
        onTap: stopAlarm,
        child: Center(
          child: Column(
            children: [
              Text(widget.settings.notificationTitle),
              Text(widget.settings.notificationBody),
              const Text('tap to stop alarm'),
            ],
          ),
        ),
      ),
    );
  }
}
