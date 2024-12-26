import 'dart:async';
import 'package:alarm/alarm.dart';
import 'package:flutter/material.dart';

import '/utils.dart';

void openAlarmPage(settings) {
  Log.debug('openAlarmPage $settings');
  if (globalNavigatorKey.currentState?.context == null)  return;
  if (settings.dateTime.isAfter(DateTime.now())) return;
  if (settings.dateTime.isBefore(
      DateTime.now().subtract(const Duration(minutes: 30)))) {
    Alarm.stop(settings.id);
    return;
  }
  ModalRoute? currentRoute = ModalRoute.of(globalNavigatorKey.currentState!.context);
  while (currentRoute?.settings.arguments is AlarmSettings
    && (currentRoute?.settings.arguments as AlarmSettings).id != settings.id)
    {
    Navigator.pop(globalNavigatorKey.currentState!.context);
    currentRoute = ModalRoute.of(globalNavigatorKey.currentState!.context);
  }
  if (currentRoute?.settings.arguments is AlarmSettings
    && (currentRoute?.settings.arguments as AlarmSettings).id == settings.id) {
    return;
  }
  Future.delayed(const Duration(minutes: 30), () => Alarm.stop(settings.id));
  globalNavigatorKey.currentState?.push(
    MaterialPageRoute<void>(
      builder: (context) => AlarmPage(settings: settings),
    ),
  );
}

class AlarmPage extends StatefulWidget {
  const AlarmPage({
    required this.settings,
    super.key,
  });

  final AlarmSettings settings;

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
