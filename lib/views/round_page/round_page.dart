import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import '/providers.dart';
import '/utils.dart';
import 'tabs/games_tab.dart';
import 'tabs/scores_tab.dart';

final roundProvider =
    StreamProvider.autoDispose.family<RoundScheduleData, RoundId>(
  (ref, roundId) async* {
    final schedule = await ref.watch(scheduleProvider.future);
    yield schedule.rounds.firstWhere((round) => round.id == roundId);
  },
);

class RoundPage extends ConsumerWidget {
  const RoundPage({super.key});

  RoundId roundId(BuildContext context) {
    return ModalRoute.of(context)?.settings.arguments as RoundId;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final round = ref.watch(roundProvider(roundId(context)));
    return round.when(
      loading: () => Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: const Text('Round'),
        ),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (error, stackTrace) => Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: const Text('Round'),
        ),
        body: ErrorScreen(error: error, stackTrace: stackTrace),
      ),
      data: (round) => DefaultTabController(
        length: 2,
        child: Scaffold(
          appBar: AppBar(
            backgroundColor: Theme.of(context).colorScheme.inversePrimary,
            title: Text(round.name),
            bottom: const TabBar(tabs: [
              Tab(text: 'Scores'),
              Tab(text: 'Games'),
            ]),
          ),
          body: TabBarView(children: [
            RoundScoresTab(round: round),
            RoundGamesTab(round: round),
          ]),
        ),
      ),
    );
  }
}
