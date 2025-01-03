import 'dart:async';
import 'dart:collection';
import 'package:alarm/alarm.dart';
import 'package:flutter/material.dart';

import '/utils.dart';

final _activeAlarms = HashSet<int>();

void openAlarmPage(AlarmSettings settings) async {
  Log.debug('openAlarmPage $settings');
  if (globalNavigatorKey.currentState?.context == null) return;
  if (settings.dateTime.isAfter(DateTime.now())) return;
  if (settings.dateTime.isBefore(
      DateTime.now().subtract(const Duration(minutes: 30)))) {
    Alarm.stop(settings.id);
    return;
  }

  if (_activeAlarms.contains(settings.id)) return;
  
  _activeAlarms.add(settings.id);
  
  await Future.delayed(const Duration(milliseconds: 100));

  Future.delayed(const Duration(minutes: 30), () {
    Alarm.stop(settings.id);
    _activeAlarms.remove(settings.id);
  });

  if (!globalNavigatorKey.currentState!.mounted) return;
  
  globalNavigatorKey.currentState?.push(
    MaterialPageRoute<void>(
      builder: (context) => AlarmPage(
        settings: settings,
        onClose: () => _activeAlarms.remove(settings.id),
      ),
    ),
  );
}

class AlarmPage extends StatefulWidget {
  const AlarmPage({
    required this.settings,
    required this.onClose,
    super.key,
  });

  final AlarmSettings settings;
  final VoidCallback onClose;

  @override
  State<AlarmPage> createState() => _AlarmPageState();
}

class _AlarmPageState extends State<AlarmPage> with WidgetsBindingObserver {
  late Timer _autoCloseTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _setAutoCloseTimer();
  }

  @override
  void dispose() {
    widget.onClose();
    WidgetsBinding.instance.removeObserver(this);
    _autoCloseTimer.cancel();
    super.dispose();
  }

  void _setAutoCloseTimer() {
    _autoCloseTimer = Timer(const Duration(minutes: 30), _closeIfExpired);
  }

  void _closeIfExpired() {
    if (mounted && _isExpired()) {
      Navigator.of(context).pop();
    }
  }

  bool _isExpired() {
    return DateTime.now().isAfter(
      widget.settings.dateTime.add(const Duration(minutes: 30)),
    );
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _closeIfExpired();
    }
  }

  @override
  Widget build(BuildContext context) {
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
                  widget.settings.notificationSettings.title,
                  softWrap: true,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 28.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  widget.settings.notificationSettings.body,
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
