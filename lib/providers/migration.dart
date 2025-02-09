import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import '/services/notification_preferences.dart';
import '/providers.dart';

const currentAppVersion = '1.0.0'; // Update this with your actual version

final migrationProvider = Provider((ref) => MigrationService(ref));

class MigrationService {
  final Ref ref;

  MigrationService(this.ref);

  Future<void> checkMigration(BuildContext context) async {
    final storedVersion = ref.read(appVersionProvider);
    final hasLegacyPrefs = ref.read(hasLegacyPreferencesProvider);

    // If we have legacy prefs, but no version number, reset FCM notifications
    if (hasLegacyPrefs && storedVersion == "0.0.0") {
      await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('App Update'),
          content: const Text(
            'The app needs to reset notification settings.'
            'We need to restart.'
          ),
          actions: [
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('OK'),
            ),
          ],
        ),
      );

      // Update stored version
      await ref.read(appVersionProvider.notifier).set(currentAppVersion);
      final service = ref.read(notificationPreferencesProvider);
      await service.resetNotifications();
    }
  }
}
