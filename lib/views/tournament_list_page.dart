import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '/providers.dart';
import '/utils.dart';
import '/views/error_view.dart';
import 'loading_view.dart';

class TournamentListPage extends ConsumerWidget {
  const TournamentListPage({super.key});

  @override
  Widget build(BuildContext context, ref) {
    final allTournamentsAsync = ref.watch(allTournamentsListProvider);
    final testMode = ref.watch(testModePrefProvider);

    return allTournamentsAsync.when(
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
            error: error,
            stackTrace: stackTrace,
          ),
      data: (_) {
        return Scaffold(
          appBar: AppBar(
            title: GestureDetector(
              onTap: () {
                // Toggle test mode on triple tap
                if (DateTime.now().difference(_lastTap).inMilliseconds < 500) {
                  _tapCount++;
                  if (_tapCount > 2) {
                    ref.read(testModePrefProvider.notifier).set(!testMode);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Test mode ${testMode ? 'disabled' : 'enabled'}'),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                    _tapCount = 0;
                  }
                } else {
                  _tapCount = 1;
                }
                _lastTap = DateTime.now();
              },
              child: const Text('Tournaments'),
            ),
          ),
          body: DefaultTabController(
            length: testMode ? 4 : 3,
            child: Column(children: [
              Material(
                color: Theme.of(context).colorScheme.inversePrimary,
                child: TabBar(tabs: [
                  const Tab(text: 'Live'),
                  const Tab(text: 'Upcoming'),
                  const Tab(text: 'Past'),
                  if (testMode) const Tab(text: 'Test'),
                ]),
              ),
              Expanded(
                child: TabBarView(children: [
                  const TournamentList(when: WhenTournament.live),
                  const TournamentList(when: WhenTournament.upcoming),
                  const PastTournamentList(),
                  if (testMode) const TournamentList(when: WhenTournament.test),
                ]),
              ),
            ]),
          ),
        );
      },
    );
  }

  static DateTime _lastTap = DateTime.now();
  static int _tapCount = 0;
}

class TournamentList extends ConsumerWidget {
  const TournamentList({required this.when, super.key});

  final WhenTournament when;

  @override
  Widget build(context, ref) {
    final tournamentId = ref.watch(tournamentIdProvider);
    final tournamentList = ref.watch(tournamentListProvider(when));
    if (tournamentList.isEmpty) {
      return const Center(child: Text('No Tournaments Found'));
    }
    return ListView(
      padding: const EdgeInsets.all(8),
      children: [
        for (final tournament in tournamentList)
          Card(
            child: ListTile(
              leading: switch (tournament.urlIcon) {
                "" => const Icon(Icons.event),
                _ => CachedNetworkImage(
                      height: 70,
                      width: 70,
                      imageUrl: tournament.urlIcon,
                      placeholder: (c, u) =>
                      const Center(
                        child: CircularProgressIndicator(),
                      ),
                      errorWidget: (c, u, e) => const Icon(Icons.error),
                      fit: BoxFit.contain,
                    ),
              },
              selected: tournamentId == tournament.id,
              title: Text(tournament.name),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(tournament.when),
                  Text(tournament.country),
                ],
              ),
              onTap: () async {
                await ref
                    .read(tournamentIdProvider.notifier) //
                    .set(tournament.id);

                if (!context.mounted) return;
                Navigator.of(context).pushNamed(ROUTES.tournament);
              },
            ),
          ),
      ],
    );
  }
}

class PastTournamentList extends ConsumerWidget {
  const PastTournamentList({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summaries = ref.watch(pastTournamentSummariesProvider);

    return summaries.when(
      loading: () => const LoadingView(),
      error: (error, stack) => ErrorView(error: error, stackTrace: stack),
      data: (summaries) => ListView.builder(
        itemCount: summaries.length,
        itemBuilder: (context, index) {
          final summary = summaries[index];
          return ListTile(
            title: Text(summary.name),
            subtitle: Text(
              '${DateFormat.yMMMd().format(summary.startDate)} - '
              '${DateFormat.yMMMd().format(summary.endDate)}\n'
              '${summary.venue}, ${summary.country}\n'
              '${summary.playerCount} players - ${summary.rules}',
            ),
            isThreeLine: true,
            onTap: () async {
              // Show loading dialog
              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (context) => const LoadingDialog(),
              );

              try {
                // Load tournament details
                await ref.read(pastTournamentDetailsProvider(summary.id).future);

                // Set the tournament ID
                await ref.read(tournamentIdProvider.notifier).set(summary.id);

                // Navigate to tournament page
                if (context.mounted) {
                  Navigator.pop(context); // Dismiss loading dialog
                  Navigator.of(context).popAndPushNamed(ROUTES.tournament);
                }
              } catch (e) {
                if (context.mounted) {
                  Navigator.pop(context); // Dismiss loading dialog
                  String msg = 'Error loading tournament: $e';
                  Log.warn(msg);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(msg)),
                  );
                }
              }
            },
          );
        },
      ),
    );
  }
}

class LoadingDialog extends StatelessWidget {
  const LoadingDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return const AlertDialog(
      content: Row(
        children: [
          CircularProgressIndicator(),
          SizedBox(width: 20),
          Text('Loading tournament data...'),
        ],
      ),
    );
  }
}
