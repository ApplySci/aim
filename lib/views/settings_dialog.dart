import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';

import '/providers.dart';
import '/services/notification_preferences.dart';

class SettingsDialog extends ConsumerWidget {
  const SettingsDialog({super.key});

  static Future<void> show(BuildContext context) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const SettingsDialog(),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alarmPref = ref.watch(alarmPrefProvider);
    final timezonePref = ref.watch(timezonePrefProvider);
    final vibratePref = ref.watch(vibratePrefProvider);
    final notificationsPref = ref.watch(notificationsPrefProvider);

    return Dialog(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Settings'),
          automaticallyImplyLeading: false,
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ),
        body: ListView(
          children: <Widget>[
            SwitchListTile(
              title: const Text('Tournament notifications'),
              subtitle: const Text('Score updates, schedule changes, and seating information'),
              value: notificationsPref,
              onChanged: (value) async {
                final service = ref.read(notificationPreferencesProvider);
                final currentAlarms = ref.read(alarmPrefProvider);
                await service.updatePreferences(
                  value 
                    ? (currentAlarms ? NotificationChoice.all : NotificationChoice.updates)
                    : (currentAlarms ? NotificationChoice.alarmsOnly : NotificationChoice.none),
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
                    final currentNotifications = ref.read(notificationsPrefProvider);
                    await service.updatePreferences(
                      value
                        ? (currentNotifications ? NotificationChoice.all : NotificationChoice.alarmsOnly)
                        : (currentNotifications ? NotificationChoice.updates : NotificationChoice.none),
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