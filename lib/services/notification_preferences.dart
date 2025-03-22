import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:restart_app/restart_app.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '/providers.dart';
import '/utils.dart';

enum NotificationChoice {
  none,
  updates,
  alarmsOnly,
  all;

  bool get wantsNotifications => this == updates || this == all;
  bool get wantsAlarms => this == alarmsOnly || this == all;
}

class NotificationPreferencesService {
  final Ref ref;

  NotificationPreferencesService(this.ref);

  Future<void> updatePreferences(NotificationChoice choice) async {
    Log.debug('in updatePreferences');
    final currentNotifications = ref.read(notificationsPrefProvider);
    final currentAlarms = ref.read(alarmPrefProvider);

    // Only update if values actually changed
    if (currentNotifications != choice.wantsNotifications) {
      Log.debug('setting notificationsPrefProvider');
      await ref.read(notificationsPrefProvider.notifier).set(
          choice.wantsNotifications);
    }

    if (currentAlarms != choice.wantsAlarms) {
      await ref.read(alarmPrefProvider.notifier).set(choice.wantsAlarms);
    }

    // Always refresh subscriptions when preferences change
    await refreshSubscriptions();
  }

  Future<void> refreshSubscriptions() async {
    Log.debug('refreshing FCM subscriptions');
    try {
      // Check if notifications are enabled first
      final notificationsEnabled = ref.read(notificationsPrefProvider);
      if (!notificationsEnabled) {
        Log.debug('Notifications disabled, skipping subscription');
        return;
      }

      // Get current tournament and player
      final tournamentId = ref.read(tournamentIdProvider);
      if (tournamentId == null) {
        Log.debug('No tournament selected, skipping subscription');
        return;
      }

      // Check if tournament is past before doing any unsubscribe operations
      final tournamentInfo = await ref.read(tournamentInfoProvider.future);
      if (tournamentInfo.status == WhenTournament.past) {
        Log.debug('Tournament is past, skipping subscription');
        return;
      }

      // Handle subscriptions in the background
      Future(() async {
        try {
          // Unsubscribe from old topics
          Log.debug('awaiting unsubscribeFromAllTopics');
          await unsubscribeFromAllTopics();

          final playerId = ref.read(selectedPlayerIdProvider);

          // Subscribe to new topics
          final fcm = ref.read(fcmProvider);
          final topics = <String>{tournamentId};
          if (playerId == null) {
            topics.add('$tournamentId-');
          } else {
            topics.add('$tournamentId-$playerId');
          }

          for (final topic in topics) {
            try {
              await fcm.subscribeToTopic(topic);
            } catch (e) {
              // Continue with other topics even if one fails
            }
          }

          // Update tracked topics
          await ref.read(fcmTopicsProvider.notifier).set(topics);
          Log.debug('subscribed to topics: $topics');
        } catch (e) {
          Log.debug('Background subscription error: $e');
        }
      });
    } catch (e) {
      Log.debug('Error in refreshSubscriptions: $e');
      // Don't rethrow - we don't want FCM errors to break the app
    }
  }

  Future<void> unsubscribeFromAllTopics() async {
    Log.debug('unsubscribing from all notification topics');
    final fcm = ref.read(fcmProvider);
    final currentTopics = ref.read(fcmTopicsProvider) ?? {};

    // Unsubscribe from all current topics
    for (final topic in currentTopics) {
      await fcm.unsubscribeFromTopic(topic);
    }

    // Clear topics in preferences
    await ref.read(fcmTopicsProvider.notifier).set({});
  }

  Future<void> resetNotifications() async {
    await unsubscribeFromAllTopics();

    // Delete FCM token
    final fcm = ref.read(fcmProvider);
    await fcm.deleteToken();

    // TEMPORARILY MODIFIED: We're commenting out the destructive parts to diagnose Android issues
    // Once we confirm if this is part of the problem, we'll restore the proper reset logic

    // Set a flag to force reinitialization on next startup
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('fcm_needs_init', true);
    Log.debug('Setting FCM reinit flag for all platforms');

    /*
    // COMMENTED OUT TEMPORARILY FOR TESTING - Will be restored later
    // This is the full destructive reset needed for proper subscription flushing

    if (Platform.isIOS) {
      // Delete Firebase instance, forcing creation of a new FID, to
      // properly wipe out all old topic subscriptions on iOS
      Log.debug('Deleting Firebase Installation (iOS only)');
      await FirebaseInstallations.instance.delete();
    } else {
      // For Android, we'll just set a flag to reinitialize on next startup
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('fcm_needs_init', true);
      Log.debug('Setting FCM reinit flag for Android');
    }
    */

    Restart.restartApp(
      // Customizing the restart notification message (only needed on iOS)
      notificationTitle: 'Restarting the World Riichi App',
      notificationBody: 'Please tap here to open the app again.',
    );

    /*
    https://pub.dev/packages/restart_app

    Add the following to the project /ios/Runner/Info.plist file.
    This will allow the app to send local notifications.
    Replace PRODUCT_BUNDLE_IDENTIFIER and example with your actual bundle identifier and URL scheme:

<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleTypeRole</key>
    <string>Editor</string>
    <key>CFBundleURLName</key>
	<!-- You can find it on /ios/project.pbxproj - 'PRODUCT_BUNDLE_IDENTIFIER' -->
    <string>[Your project PRODUCT_BUNDLE_IDENTIFIER value]</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <!-- Your app title -->
      <string>example</string>
    </array>
  </dict>
</array>

*/

  }
}

final notificationPreferencesProvider = Provider((ref) => NotificationPreferencesService(ref));
