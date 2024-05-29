import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/utils.dart';
import 'tabs/info_tab.dart';
import 'tabs/player_list_tab.dart';
import 'tabs/round_list_tab.dart';
import 'tabs/score_tab.dart';

final pageProvider = StateProvider((ref) => 0);

class TournamentPage extends ConsumerWidget {
  const TournamentPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final page = ref.watch(pageProvider);
    final tournament = ref.watch(tournamentProvider);

    return tournament.when(
      skipLoadingOnReload: true,
      loading: () => Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: const Text('Tournament'),
        ),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (error, stackTrace) => Scaffold( // uses ErrorScreen
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: const Text('Tournament'),
        ),
        body: ErrorScreen(error: error, stackTrace: stackTrace),
      ),
      data: (tournament) => Scaffold(
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
          index: page,
          children: const [
            Seating(),
            ScoreTable(),
            Players(),
            TournamentInfo(),
          ],
        ),
        bottomNavigationBar: BottomNavigationBar(
          type: BottomNavigationBarType.fixed,
          currentIndex: page,
          onTap: (index) => ref
              .read(pageProvider.notifier) //
              .state = index,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.airline_seat_recline_normal_outlined),
              label: 'Seating',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.score),
              label: 'Scores',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.people),
              label: 'Players',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.info),
              label: 'Info',
            ),
          ],
        ),
      ),
    );
  }
}
