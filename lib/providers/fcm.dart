import 'dart:async';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final fcmProvider = Provider((ref) => FirebaseMessaging.instance);

final fcmTokenProvider = StreamProvider((ref) async* {
  final fcm = ref.watch(fcmProvider);
  yield await fcm.getToken() ?? '';
  yield* FirebaseMessaging.instance.onTokenRefresh;
});

final fcmMessagesProvider = StreamProvider((ref) async* {
  final fcm = ref.watch(fcmProvider);
  final initialMessage = await fcm.getInitialMessage();
  if (initialMessage != null) yield initialMessage;

  final controller = StreamController<RemoteMessage>();
  ref.onDispose(() => controller.close());

  FirebaseMessaging.onMessage.pipe(controller);
  FirebaseMessaging.onMessageOpenedApp.pipe(controller);

  yield* controller.stream;
});
