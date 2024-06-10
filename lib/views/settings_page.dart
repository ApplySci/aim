import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(context, ref) {
    final alarmPref = ref.watch(alarmPrefProvider);
    final timezonePref = ref.watch(timezonePrefProvider);
    final scorePref = ref.watch(scorePrefProvider);
    final seatingPref = ref.watch(seatingPrefProvider);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Settings'),
      ),
      body: Column(
        children: <Widget>[
          SwitchListTile(
            title: const Text('Alarms for start of hanchan'),
            value: alarmPref,
            onChanged: (value) => ref
                .read(alarmPrefProvider.notifier) //
                .set(value),
          ),
          SwitchListTile(
            title:
                const Text('Use event timezone (rather than device timezone)'),
            value: timezonePref,
            onChanged: (value) => ref
                .read(timezonePrefProvider.notifier) //
                .set(value),
          ),
          /*   commented out as they're not currently used
          SwitchListTile(
            title: const Text('Notifications for updated scores'),
            value: scorePref,
            onChanged: (value) => ref
                .read(scorePrefProvider.notifier) //
                .set(value),
          ),
          SwitchListTile(
            title:
                const Text('Notifications for changes to seating & schedule'),
            value: seatingPref,
            onChanged: (value) => ref
                .read(seatingPrefProvider.notifier) //
                .set(value),
          ),
           */
        ],
      ),
    );
  }
}
