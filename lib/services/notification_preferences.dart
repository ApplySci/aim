import 'package:flutter_riverpod/flutter_riverpod.dart';
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
    Log.debug('Updating notification preferences: $choice');
    
    // Update notification and alarm preferences
    await ref.read(notificationsPrefProvider.notifier).set(choice.wantsNotifications);
    await ref.read(alarmPrefProvider.notifier).set(choice.wantsAlarms);
    
    // Handle FCM topic subscriptions
    if (!choice.wantsNotifications) {
      await unsubscribeFromAllTopics();
    }
  }

  Future<void> unsubscribeFromAllTopics() async {
    final fcm = ref.read(fcmProvider);
    final currentTopics = ref.read(fcmTopicsProvider) ?? {};

    // Unsubscribe from all current topics
    for (final topic in currentTopics) {
      await fcm.unsubscribeFromTopic(topic);
    }

    // Clear topics in preferences
    await ref.read(fcmTopicsProvider.notifier).set({});
  }
}

final notificationPreferencesProvider = Provider((ref) => NotificationPreferencesService(ref)); 