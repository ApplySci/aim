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
    final storedVersion = ref.read(appVersionProvider);Log.debug('***** Stored version: $storedVersion');

    // If we have legacy prefs, but no version number, reset FCM notifications
    if (storedVersion == "0.0.0") {
      // Update stored version
      await ref.read(appVersionProvider.notifier).set(currentAppVersion);
      final service = ref.read(notificationPreferencesProvider);
      await service.resetNotifications();
    }
  }
}
