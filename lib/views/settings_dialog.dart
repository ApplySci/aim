import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';

import '/providers.dart';
import '/services/notification_preferences.dart';
import 'loading_overlay.dart';
import '/utils.dart';

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
    final testMode = ref.watch(testModePrefProvider);

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
            const SizedBox(height: 96),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.red,
                  side: const BorderSide(color: Colors.red),
                ),
                icon: const Icon(Icons.warning),
                onPressed: () async {
                  OverlayEntry? overlayEntry;

                  try {
                    overlayEntry = OverlayEntry(
                      builder: (context) => Container(
                        color: Colors.black54,
                        child: const LoadingOverlay(
                          message: 'Resetting notification settings...',
                        ),
                      ),
                    );
                    Overlay.of(context).insert(overlayEntry);

                    final service = ref.read(notificationPreferencesProvider);
                    await service.resetNotifications();
                  } catch (e) {
                    overlayEntry?.remove();
                    if (context.mounted) {
                      Navigator.of(context).pop(); // Dismiss settings dialog
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('Error resetting notifications: $e'),
                        ),
                      );
                    }
                  }
                },
                label: const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8.0),
                  child: Text('Reset All Notification Settings (restarts the app)'),
                ),
              ),
            ),
            const SizedBox(height: 20),
            if (testMode) ...[
              ListTile(
                title: const Text('View Debug Logs'),
                trailing: TextButton(
                  onPressed: () async {
                    await Log.clearAllLogs();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Debug logs cleared')),
                      );
                    }
                  },
                  child: const Text('Clear Logs'),
                ),
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Debug Logs'),
                      content: SingleChildScrollView(
                        child: Text(
                          Log.getLogs().join('\n'),
                        ),
                      ),
                      actions: [
                        TextButton(
                          onPressed: () async {
                            await Log.cleanupOldLogs();
                            if (context.mounted) {
                              Navigator.pop(context);
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Cleaned up old logs')),
                              );
                            }
                          },
                          child: const Text('Clean Old Logs'),
                        ),
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('Close'),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ],
          ],
        ),
      ),
    );
  }
}
