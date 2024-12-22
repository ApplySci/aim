import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/utils.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import 'tabs/info_tab.dart';
import 'tabs/player_list_tab.dart';
import 'tabs/round_list_tab.dart';
import 'tabs/score_tab.dart';

final pageProvider = StateProvider((ref) => 0);
final initialTabProvider = StateProvider<TournamentTab?>((ref) => null);

enum TournamentTab {
  scores,
  info,
  seating,
  players;

  int toIndex(WhenTournament tournamentStatus) {
    // If tournament hasn't started yet, scores tab isn't shown
    if (tournamentStatus == WhenTournament.upcoming) {
      return switch (this) {
        TournamentTab.scores => 0,  // Default to info if scores not available
        TournamentTab.info => 0,
        TournamentTab.seating => 1,
        TournamentTab.players => 2,
      };
    }
    return switch (this) {
      TournamentTab.scores => 0,
      TournamentTab.info => 1,
      TournamentTab.seating => 2,
      TournamentTab.players => 3,
    };
  }

  static TournamentTab fromNotificationType(String type) {
    return switch (type) {
      'scores' => TournamentTab.scores,
      'info' => TournamentTab.info,
      'seating' => TournamentTab.seating,
      'players' => TournamentTab.players,
      _ => TournamentTab.info,
    };
  }
}

class TournamentPage extends ConsumerWidget {
  const TournamentPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final page = ref.watch(pageProvider);
    final tournament = ref.watch(tournamentProvider);
    final tournamentStatus = ref.watch(tournamentStatusProvider).valueOrNull ?? WhenTournament.upcoming;

    // Check for initial tab from notification
    final initialTab = ref.watch(initialTabProvider);
    if (initialTab != null) {
      // Clear the initial tab so it's only used once
      ref.read(initialTabProvider.notifier).state = null;
      // Set the page
      ref.read(pageProvider.notifier).state = initialTab.toIndex(tournamentStatus);
    }

    return tournament.when(
      skipLoadingOnReload: true,
      loading: () => const LoadingScaffold(
        title: Text('Tournament'),
      ),
      error: (error, stackTrace) => ErrorScaffold(
        title: const Text('Tournament'),
        error: error,
        stackTrace: stackTrace,
      ),
      data: (tournament) {
        final navItems = [
          if (tournamentStatus != WhenTournament.upcoming)
            const BottomNavigationBarItem(
              icon: Icon(Icons.score),
              label: 'Scores',
            ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.info),
            label: 'Info',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.airline_seat_recline_normal_outlined),
            label: 'Seating',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.people),
            label: 'Players',
          ),
        ];

        return Scaffold(
          appBar: AppBar(
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
            children: [
              if (tournamentStatus != WhenTournament.upcoming)
                const ScoreTable(),
              const TournamentInfo(),
              const Seating(),
              const Players(),
            ],
          ),
          bottomNavigationBar: BottomNavigationBar(
            type: BottomNavigationBarType.fixed,
            currentIndex: page,
            onTap: (index) => ref.read(pageProvider.notifier).state = index,
            items: navItems,
          ),
        );
      },
    );
  }
}
