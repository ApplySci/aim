import 'package:collection/collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import '/providers.dart';
import 'tabs/games_tab.dart';
import 'tabs/scores_tab.dart';
import '/utils.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import '/views/tab_scaffold.dart';

final roundProvider =
    StreamProvider.autoDispose.family<RoundScheduleData, String>(
  (ref, roundId) async* {
    final schedule = await ref.watch(scheduleProvider.future);
    Log.debug('Looking for round $roundId (${roundId.runtimeType})');
    Log.debug('Available rounds: ${schedule.rounds.map((r) => "${r.id} (${r.id.runtimeType})")}');

    final round = schedule.rounds.firstWhereOrNull(
      (round) => round.id.toString() == roundId.toString()
    );
    if (round == null) {
      throw Exception('Round $roundId not found');
    }
    yield round;
  },
);

class RoundPage extends ConsumerWidget {
  const RoundPage({super.key});

  String roundId(BuildContext context) {
    return ModalRoute.of(context)?.settings.arguments as String;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final round = ref.watch(roundProvider(roundId(context)));
    return PopScope(
      canPop: true,
      onPopInvoked: (didPop) async {
        if (didPop) return;
        
        if (context.mounted) {
          await Navigator.of(context).maybePop();
        }
      },
      child: round.when(
        loading: () => const LoadingScaffold(
          title: Text('Round'),
        ),
        error: (error, stackTrace) => ErrorScaffold(
          title: const Text('Round'),
          error: error,
          stackTrace: stackTrace,
        ),
        data: (round) => TabScaffold(
          title: Text(round.name),
          tabs: const [
            Tab(text: 'Games'),
            Tab(text: 'Scores'),
          ],
          children: [
            RoundGamesTab(round: round),
            RoundScoresTab(round: round),
          ],
        ),
      ),
    );
  }
}
