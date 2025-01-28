import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';

import '/providers.dart';
import '/views/app_bar.dart';
import '/services/notification_preferences.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(context, ref) {
    final alarmPref = ref.watch(alarmPrefProvider);
    final timezonePref = ref.watch(timezonePrefProvider);
    final vibratePref = ref.watch(vibratePrefProvider);
    final notificationsPref = ref.watch(notificationsPrefProvider);

    return PopScope(
      canPop: true,
      child: Scaffold(
        appBar: CustomAppBar(
          title: const Text('Settings'),
          showHomeButton: false,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ),
        body: Column(
          children: <Widget>[
            SwitchListTile(
              title: const Text('Tournament notifications'),
              subtitle: const Text('Score updates, schedule changes, and seating information'),
              value: notificationsPref,
              onChanged: (value) async {
                final service = ref.read(notificationPreferencesProvider);
                await service.updatePreferences(
                  value ? NotificationChoice.updates : NotificationChoice.none,
                );
              },
            ),
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
                    final service = ref.read(notificationPreferencesProvider);
                    await service.updatePreferences(
                      value ? NotificationChoice.all : NotificationChoice.updates,
                    );
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
      ),
    );
  }
}