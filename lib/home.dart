import 'package:flutter/material.dart';

import 'frame.dart';
import 'tournaments.dart';

class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return navFrame(context, const TournamentList());
  }
}
