import 'dart:async';

import 'package:alarm/alarm.dart';
import 'package:alarm/model/alarm_settings.dart';
import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'alarm.dart';
import 'store.dart';
import 'utils.dart';
import 'venue.dart';

StreamSubscription<AlarmSettings>? alarmListener;

Widget navFrame(BuildContext context, Widget body) {
  // Unhandled Exception: Looking up a deactivated widget's ancestor is unsafe.
  // E/flutter ( 5008): At this point the state of the widget's element tree is no longer stable.
  Future<void> alarmIsRinging(AlarmSettings settings) async {
    await globalNavigatorKey.currentState?.push(
      MaterialPageRoute<void>(
        builder: (context) => AlarmScreen(settings: settings),
      ),
    );
  }

  alarmListener ??= Alarm.ringStream.stream.listen(alarmIsRinging);

  return StoreConnector<AllState, Map<String, dynamic>>(
    converter: (store) {
      return store.state.tournament;
    },
    builder: (BuildContext context, Map<String, dynamic> t) {
      final List<Widget> actions = [];

      actions.addAll([
        IconButton(
          icon: const Icon(Icons.score),
          onPressed: () => Navigator.pushNamed(context, ROUTES.scoreTable),
        ),
        IconButton(
          icon: const Icon(Icons.airline_seat_recline_normal_outlined),
          onPressed: () => Navigator.pushNamed(context, ROUTES.seating),
        ),
        IconButton(
          icon: const Icon(Icons.location_on),
          onPressed: t['address'] == null ? null : () => openMap(t['address']),
        ),
        IconButton(
          icon: const Icon(Icons.info),
          onPressed: () => Navigator.pushNamed(context, ROUTES.info),
        ),
        IconButton(
          icon: const Icon(Icons.people),
          onPressed: () => Navigator.pushNamed(context, ROUTES.players),
        ),
        IconButton(
          icon: const Icon(Icons.settings),
          onPressed: () => Navigator.pushNamed(context, ROUTES.settings),
        ),
        IconButton(
          icon: const Icon(Icons.home_filled),
          onPressed: () => Navigator.pushNamed(context, ROUTES.home),
        ),
      ]);

      return Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          primary: true,
          title: null,
          actions: actions,
        ),
        body: SingleChildScrollView(
          scrollDirection: Axis.vertical,
          child: Column(
            children: [
              Center(
                child: Text(
                  t['name'],
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                  ),
                ),
              ),
              body,
            ],
          ),
        ),
      );
    },
  );
}
