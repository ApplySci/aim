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
import '../tab_scaffold.dart';

class PlayerPage extends ConsumerWidget {
  const PlayerPage({
    super.key,
  });

  void abortBuild(BuildContext context, String msg) {
    Future.delayed(Durations.short1, () {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg)),
      );
      Navigator.pop(context);
    });
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return PopScope(
      canPop: true,
      onPopInvoked: (didPop) async {
        if (didPop) return;
        
        if (context.mounted) {
          await Navigator.of(context).maybePop();
        }
      },
      child: Consumer(
        builder: (context, ref, child) {
          final args = ModalRoute.of(context)!.settings.arguments as Map;
          PlayerId? playerId = args['playerId'];
          int? seat = args['seat'];
          PlayerData? playerData;
          AsyncValue<PlayerRankings> playerScore;

          if (playerId == null) {
            if (seat == null) {
              abortBuild(context, 'No way to identify this player');
            } else {
              final seatMap = ref.watch(seatMapProvider).valueOrNull;
              if (seatMap != null && seatMap.containsKey(seat)) {
                playerId = seatMap[seat]!.id;
              } else {
                abortBuild(context, 'No seating available yet');
              }
            }
          }

          final playerMap = ref.watch(playerMapProvider).valueOrNull;
          if (playerMap != null && playerMap.containsKey(playerId)) {
            playerData = playerMap[playerId];
          }
          if (seat == null) {
            try {
              seat = playerData!.seat;
            } catch(e) {
              abortBuild(context, 'Player not found');
            }
          }

          try {
            playerScore = ref.watch(playerScoreProvider(seat!));
          } catch(e) {
            abortBuild(context, 'Scores not available');
            return const Text('failed');
          }

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
              final isSelected = ref.watch(
                selectedPlayerIdProvider.select((id) => id == playerId),
              );

              return TabScaffold(
                title: Text(playerData!.name),
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
                tabs: const [
                  Tab(text: 'Stats'),
                  Tab(text: 'Schedule'),
                  Tab(text: 'Scores'),
                  Tab(text: 'Games'),
                ],
                children: [
                  PlayerStatsTab(player: player),
                  PlayerScheduleTab(player: player.games),
                  PlayerScoreTab(player: player.games),
                  PlayerGameTab(player: player.games),
                ],
              );
            });
        },
      ),
    );
  }
}
