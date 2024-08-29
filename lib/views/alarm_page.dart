import 'dart:async';
import 'package:alarm/alarm.dart';
import 'package:flutter/material.dart';

import '/utils.dart';

class AlarmPage extends StatefulWidget {
  const AlarmPage({
    required this.settings,
    super.key,
  });

  final AlarmSettings settings;

  @override
  State<AlarmPage> createState() => _AlarmPageState();
}

class _AlarmPageState extends State<AlarmPage> {
  late Timer _autoCloseTimer;

  @override
  void initState() {
    super.initState();
    _autoCloseTimer = Timer(const Duration(minutes: 30), () {
      if (mounted) {
        Navigator.of(context).pop();
      }
    });
  }

  @override
  void dispose() {
    _autoCloseTimer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Log.debug('building alarm page');
    Log.debug(widget.settings.toString());
    return PopScope(
      onPopInvokedWithResult: (didPop, _) => Alarm.stop(widget.settings.id),
      child: Dialog(
        child: InkWell(
          onTap: () => Navigator.pop(context),
          child: Container(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(),
                Text(
                  widget.settings.notificationTitle,
                  softWrap: true,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 28.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  widget.settings.notificationBody,
                  softWrap: true,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 28.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                const Text(
                  'tap to dismiss',
                  textAlign: TextAlign.center,
                ),
                const Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
