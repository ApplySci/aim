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
  @override
  Widget build(BuildContext context) {
    return PopScope(
      onPopInvoked: (didPop) => Alarm.stop(widget.settings.id),
      child: Dialog(
        child: InkWell(
          onTap: () => Navigator.pop(context),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
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
