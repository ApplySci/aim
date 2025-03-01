import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';

import '/providers.dart';
import '/services/notification_preferences.dart';
import '/utils.dart';

const currentAppVersion = '1.0.0'; // Update this with your actual version

final migrationProvider = Provider((ref) => MigrationService(ref));

class MigrationService {
  final Ref ref;

  MigrationService(this.ref);

  Future<void> checkMigration(BuildContext context) async {
    final storedVersion = ref.read(appVersionProvider);
    Log.debug('Checking migration. Stored version: $storedVersion');

    // If we have legacy prefs, but no version number, reset FCM notifications
    if (storedVersion == "0.0.0") {
      await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (dialogContext) => MaterialApp(
          home: Builder(
            builder: (innerContext) => AlertDialog(
              title: const Text('App Update'),
              content: const Text(
                'The app needs to reset notification settings. '
                'We need to restart.'
              ),
              actions: [
                FilledButton(
                  onPressed: () => Navigator.pop(dialogContext, true),
                  child: const Text('OK'),
                ),
              ],
            ),
          ),
          debugShowCheckedModeBanner: false,
        ),
      );

      // Update stored version
      await ref.read(appVersionProvider.notifier).set(currentAppVersion);
      final service = ref.read(notificationPreferencesProvider);
      await service.resetNotifications();
    }
  }
}
