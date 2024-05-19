import 'package:firebase_core/firebase_core.dart';
import 'package:permission_handler/permission_handler.dart';

import 'firebase_options.dart';
import 'utils.dart';

Future<void> setNotifierEvents() async {
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  await messaging.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false, // this is for emergency services and the like. Not us
    provisional: false,
    sound: true,
  );

  final status = await Permission.scheduleExactAlarm.status;
  if (status.isDenied) {
    await Permission.scheduleExactAlarm.request();
  }
}
