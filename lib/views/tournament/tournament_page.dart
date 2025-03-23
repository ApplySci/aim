import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/utils.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import '/views/app_bar.dart';
import 'tabs/info_tab.dart';
import 'tabs/player_list_tab.dart';
import 'tabs/round_list_tab.dart';
import 'tabs/score_tab.dart';
import '/views/settings_dialog.dart';

final pageProvider = StateProvider((ref) => 0);

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
  
  // Track whether we've already handled the initial tab selection
  static bool _initialTabHandled = false;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final page = ref.watch(pageProvider);
    final tournament = ref.watch(tournamentProvider);
    final info = ref.watch(tournamentInfoProvider);

    // Handle initial tab from notification, but only once
    final args = ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
    if (!_initialTabHandled && args != null && args['initial_tab'] is String) {
      _initialTabHandled = true;
      final tab = args['initial_tab'] as String;
      final status = info.valueOrNull?.status ?? WhenTournament.upcoming;
      final index = TournamentTab.fromNotificationType(tab).toIndex(status);
      Future(() => ref.read(pageProvider.notifier).state = index);
      Log.debug('Set initial tab to $tab (index $index) from notification');
    }

    return info.when(
      loading: () => const LoadingScaffold(title: Text('Tournament')),
      error: (error, stack) => ErrorScaffold(
        title: const Text('Tournament'),
        error: error,
        stackTrace: stack,
      ),
      data: (info) {
        final navItems = [
          if (info.status != WhenTournament.upcoming)
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
            return PopScope(
              canPop: true,
              onPopInvoked: (didPop) async {
                if (didPop) return;

                if (context.mounted) {
                  await Navigator.of(context).pushReplacementNamed(ROUTES.tournaments);
                }
              },
              child: Scaffold(
                appBar: CustomAppBar(
                  title: Text(tournament.name),
                  actions: [
                    IconButton(
                      icon: const Icon(Icons.settings),
                      onPressed: () => SettingsDialog.show(context),
                    ),
                  ],
                ),
                body: IndexedStack(
                  index: page,
                  children: [
                    if (info.status != WhenTournament.upcoming)
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
              ),
            );
          },
        );
      },
    );
  }
}
