import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'store.dart';
import 'utils.dart';
import 'venue.dart';

Widget navFrame(BuildContext context, Widget body) {

  return StoreConnector<AllState, Map<String,dynamic>>(
    converter: (store) {
      return store.state.tournament;
    },
    builder: (BuildContext context, Map<String,dynamic> t) {
      final List<Widget> actions = [];

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
        onPressed: () => openMap(t['address'])
      ));
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
      if (kDebugMode) {
        actions.add(IconButton(
          icon: const Icon(Icons.home_filled),
          onPressed: () => Navigator.pushNamed(context, ROUTES.home),
        ));
      }

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
              Text(
                t['name'],
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 20,
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
