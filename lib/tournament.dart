import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'info.dart';
import 'player_list.dart';
import 'score_table.dart';
import 'seats.dart';
import 'store.dart';
import 'utils.dart';

typedef TournamentPageState = ({
  TournamentState tournament,
  int pageIndex,
});

class TournamentPage extends StatelessWidget {
  const TournamentPage({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, TournamentPageState>(
      converter: (store) => (
        tournament: store.state.tournament!,
        pageIndex: store.state.pageIndex,
      ),
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            backgroundColor: Theme.of(context).colorScheme.inversePrimary,
            title: Text(state.tournament.name),
            actions: [
              IconButton(
                icon: const Icon(Icons.settings),
                onPressed: () => Navigator.pushNamed(context, ROUTES.settings),
              ),
            ],
          ),
          body: IndexedStack(
            index: state.pageIndex,
            children: const [
              Seating(),
              Players(),
              ScoreTable(),
              TournamentInfo(),
            ],
          ),
          bottomNavigationBar: BottomNavigationBar(
            type: BottomNavigationBarType.fixed,
            currentIndex: state.pageIndex,
            onTap: (index) => store.dispatch(
              SetPageIndexAction(pageIndex: index),
            ),
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
