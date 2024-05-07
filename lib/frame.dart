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

  Future<void> alarmIsRinging(AlarmSettings settings) async {
    await Navigator.push(
      context,
      MaterialPageRoute<void>(
        builder: (context) => AlarmScreen(settings: settings),
      ),
    );
  }

  // TODO watch out for
  //  throw StateError("Stream has already been listened to.")
  // did the alarm package example use shared_preferences for this???
  alarmListener ??= Alarm.ringStream.stream.listen(alarmIsRinging);

  return StoreConnector<AllState, Map<String, dynamic>>(
    converter: (store) {
      return store.state.tournament;
    },
    builder: (BuildContext context, Map<String, dynamic> t) {
      final List<Widget> actions = [];

/*
      actions.add(const IconButton(
        icon: Icon(Icons.refresh),
        onPressed: null, // TODO add refresh action
      ));
 */
      actions.add(IconButton(
        icon: const Icon(Icons.score),
        onPressed: () => Navigator.pushNamed(context, ROUTES.scoreTable),
      ));
      actions.add(IconButton(
        icon: const Icon(Icons.airline_seat_recline_normal_outlined),
        onPressed: () => Navigator.pushNamed(context, ROUTES.seating),
      ));
      actions.add(IconButton(
          icon: const Icon(Icons.location_on),
          onPressed: t['address'] == null ? null : () => openMap(t['address'])));
      actions.add(IconButton(
        icon: const Icon(Icons.info),
        onPressed: () => Navigator.pushNamed(context, ROUTES.info),
      ));
      actions.add(IconButton(
        icon: const Icon(Icons.people),
        onPressed: () => Navigator.pushNamed(context, ROUTES.players),
      ));
      actions.add(IconButton(
        icon: const Icon(Icons.settings),
        onPressed: () => Navigator.pushNamed(context, ROUTES.settings),
      ));
      actions.add(IconButton(
        icon: const Icon(Icons.home_filled),
        onPressed: () => Navigator.pushNamed(context, ROUTES.home),
      ));

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
