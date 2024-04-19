import 'package:flutter/material.dart';

import 'utils.dart';
import 'venue.dart';

Widget Frame(BuildContext context, Widget body) {
  final List<Widget> actions = [];

  actions.add(IconButton(
    icon: const Icon(Icons.home_filled),
    onPressed: () {
      Navigator.pushNamed(context, ROUTES.home);
    },
  ));
  actions.add(IconButton(
    icon: const Icon(Icons.location_on),
    onPressed: () {
      // TODO remove hard coding!
      openMap("The Crows Nest, Victoria Cross Road, Cork, Ireland");
    },
  ));
  actions.add(IconButton(
    icon: const Icon(Icons.airline_seat_recline_normal_outlined),
    onPressed: () {
      Navigator.pushNamed(context, ROUTES.seating);
    },
  ));
  actions.add(IconButton(
    icon: const Icon(Icons.people),
    onPressed: () {
      Navigator.pushNamed(context, ROUTES.players);
    },
  ));
  actions.add(IconButton(
    icon: const Icon(Icons.score),
    onPressed: () {
      Navigator.pushNamed(context, ROUTES.scoreTable);
    },
  ));
  actions.add(IconButton(
    icon: const Icon(Icons.settings),
    onPressed: () {
      Navigator.pushNamed(context, ROUTES.settings);
    },
  ));

  return Scaffold(
    appBar: AppBar(
      backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      primary: true,
      actions: actions,
    ),
    body: body,
  );
}
