import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';

import '/providers.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(context, ref) {
    final alarmPref = ref.watch(alarmPrefProvider);
    final timezonePref = ref.watch(timezonePrefProvider);
    final vibratePref = ref.watch(vibratePrefProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: Column(
        children: <Widget>[
          FutureBuilder<bool>(
            future: Permission.scheduleExactAlarm.isPermanentlyDenied,
            builder: (context, snapshot) {
              if (snapshot.hasData && snapshot.data!) {
                return ListTile(
                  title: const Text('Alarms for start of hanchan'),
                  subtitle: const Text(
                    'Alarm permission permanently denied. Enable in system settings to use alarms.',
                  ),
                  trailing: TextButton(
                    onPressed: openAppSettings,
                    child: const Text('Open Settings'),
                  ),
                );
              }
              return SwitchListTile(
                title: const Text('Alarms for start of hanchan'),
                value: alarmPref,
                onChanged: (value) async {
                  if (value) {
                    final status = await Permission.scheduleExactAlarm.request();
                    if (status.isDenied) {
                      ref.read(alarmPrefProvider.notifier).set(false);
                      return;
                    }
                  }
                  ref.read(alarmPrefProvider.notifier).set(value);
                },
              );
            },
          ),
          SwitchListTile(
            title: const Text('Vibrate on alarm'),
            value: vibratePref,
            onChanged: (value) => ref
                .read(vibratePrefProvider.notifier)
                .set(value),
          ),
          SwitchListTile(
            title: const Text('Use event timezone (rather than device timezone)'),
            value: timezonePref,
            onChanged: (value) => ref
                .read(timezonePrefProvider.notifier)
                .set(value),
          ),
        ],
      ),
    );
  }
}