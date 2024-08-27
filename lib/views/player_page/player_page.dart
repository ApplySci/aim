import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import '/providers.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import 'tabs/games_tab.dart';
import 'tabs/schedule_tab.dart';
import 'tabs/scores_tab.dart';
import 'tabs/stats_tab.dart';

class PlayerPage extends ConsumerWidget {
  const PlayerPage({
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final args = ModalRoute.of(context)!.settings.arguments as Map;
    PlayerId? playerId;
    int? seat;

    if (args.containsKey('playerId')) {
      playerId = args['playerId'];
      // Get seat from playerId using playerMapProvider
      final playerMap = ref.watch(playerMapProvider).valueOrNull;
      if (playerMap != null && playerMap.containsKey(playerId)) {
        seat = playerMap[playerId]!.seat;
      } else {
        return const Center(child: Text('No seating or scores available yet'));
      }
    } else {
      seat = args['seat'];
    }

    // Use seat if available, otherwise fallback to the first player's seat
    final playerScore = ref.watch(playerScoreProvider(seat ?? 1));

    return playerScore.when(
        skipLoadingOnReload: true,
        loading: () => const LoadingScaffold(
              title: Text('Player'),
            ),
        error: (error, stackTrace) => ErrorScaffold(
              title: const Text('Player'),
              error: error,
              stackTrace: stackTrace,
            ),
        data: (player) {
          PlayerId playerId = player.games.id;
          final isSelected = ref.watch(
            selectedPlayerIdProvider.select((id) => id == playerId),
          );

          return DefaultTabController(
            length: 4,
            child: Scaffold(
              appBar: AppBar(
                title: Text(player.games.name),
                actions: [
                  IconButton(
                    onPressed: () {
                      final selectedPlayerIdNotifier =
                          ref.read(selectedPlayerIdProvider.notifier);
                      if (isSelected) {
                        selectedPlayerIdNotifier.set(null);
                      } else {
                        selectedPlayerIdNotifier.set(playerId);
                      }
                    },
                    icon: isSelected
                        ? const Icon(Icons.favorite)
                        : const Icon(Icons.favorite_border),
                  ),
                ],
                bottom: const TabBar(tabs: [
                  Tab(text: 'Stats'),
                  Tab(text: 'Schedule'),
                  Tab(text: 'Scores'),
                  Tab(text: 'Games'),
                ]),
              ),
              body: TabBarView(children: [
                PlayerStatsTab(player: player),
                PlayerScheduleTab(player: player.games),
                PlayerScoreTab(player: player.games),
                PlayerGameTab(player: player.games),
              ]),
            ),
          );
        });
  }
}
