import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'info.dart';
import 'player_list.dart';
import 'score_table.dart';
import 'seats.dart';
import 'store.dart';
import 'utils.dart';

class TournamentPage extends StatefulWidget {
  const TournamentPage({super.key});

  @override
  State<TournamentPage> createState() => _TournamentPageState();
}

class _TournamentPageState extends State<TournamentPage> {
  int pageIndex = 0;

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, TournamentState?>(
      distinct: true,
      converter: (store) => store.state.tournament,
      builder: (context, tournament) {
        if (tournament == null) {
          return const Center(child: CircularProgressIndicator());
        }

        return Scaffold(
          appBar: AppBar(
            backgroundColor: Theme.of(context).colorScheme.inversePrimary,
            title: Text(tournament.name),
            actions: [
              IconButton(
                icon: const Icon(Icons.settings),
                onPressed: () => Navigator.pushNamed(context, ROUTES.settings),
              ),
            ],
          ),
          body: IndexedStack(
            index: pageIndex,
            children: const [
              Seating(),
              Players(),
              ScoreTable(),
              TournamentInfo(),
            ],
          ),
          bottomNavigationBar: BottomNavigationBar(
            type: BottomNavigationBarType.fixed,
            currentIndex: pageIndex,
            onTap: (index) => setState(() => pageIndex = index),
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.airline_seat_recline_normal_outlined),
                label: 'Seatings',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.people),
                label: 'Players',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.score),
                label: 'Scores',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.info),
                label: 'Info',
              ),
            ],
          ),
        );
      },
    );
  }
}
