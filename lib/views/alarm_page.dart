import 'package:alarm/alarm.dart';
import 'package:flutter/material.dart';

import '/utils.dart';

class AlarmPage extends StatelessWidget {
  const AlarmPage({
    required this.settings,
    super.key,
  });

  final AlarmSettings settings;

  @override
  Widget build(BuildContext context) {
    Log.debug('building alarm page');
    Log.debug(settings.toString());
    return PopScope(
      onPopInvoked: (didPop) => Alarm.stop(settings.id),
      // onPopInvokedWithResult: (didPop, _) => Alarm.stop(settings.id), // breaking change, not yet in Flutter release
      child: Dialog(
        child: InkWell(
          onTap: () => Navigator.pop(context),
          child: Container(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(),
                Text(
                  settings.notificationTitle,
                  softWrap: true,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 28.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  settings.notificationBody,
                  softWrap: true,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 28.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                const Text(
                  'tap to dismiss',
                  textAlign: TextAlign.center,
                ),
                const Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
