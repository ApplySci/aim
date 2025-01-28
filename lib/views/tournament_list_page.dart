import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '/models.dart';
import '/providers.dart';
import 'loading_view.dart';
import '/services/notification_preferences.dart';
import 'tab_scaffold.dart';
import '/utils.dart';
import '/views/error_view.dart';
import '/views/settings_dialog.dart';

class TournamentListPage extends ConsumerWidget {
  const TournamentListPage({super.key});

  @override
  Widget build(BuildContext context, ref) {
    final allTournamentsAsync = ref.watch(allTournamentsListProvider);
    final testMode = ref.watch(testModePrefProvider);
    final rulesFilter = ref.watch(rulesFilterProvider);

    return PopScope(
      canPop: false,
      child: allTournamentsAsync.when(
        loading: () => const LoadingView(),
        error: (error, stackTrace) => ErrorView(
          error: error,
          stackTrace: stackTrace,
        ),
        data: (_) {
          return TabScaffold(
            title: GestureDetector(
              onTap: () {
                // Toggle test mode on triple tap
                if (DateTime.now().difference(_lastTap).inMilliseconds < 500) {
                  _tapCount++;
                  if (_tapCount > 2) {
                    ref.read(testModePrefProvider.notifier).set(!testMode);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                            'Test mode ${testMode ? 'disabled' : 'enabled'}'),
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
            automaticallyImplyLeading: false,
            actions: [
              IconButton(
                icon: const Icon(Icons.settings),
                onPressed: () => SettingsDialog.show(context),
              ),
            ],
            filterBar: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4.0),
              child: Wrap(
                spacing: 4.0,
                children: [
                  for (final rules in TournamentRules.values)
                    FilterChip(
                      selected: rulesFilter.contains(rules),
                      showCheckmark: false,
                      label: Text(rules.displayName),
                      labelStyle: TextStyle(
                        color: rulesFilter.contains(rules)
                            ? Theme.of(context).colorScheme.onPrimary
                            : Theme.of(context).colorScheme.onSurface,
                      ),
                      selectedColor: Theme.of(context).colorScheme.primary,
                      backgroundColor: Theme.of(context).colorScheme.surface,
                      onSelected: (selected) {
                        final newFilter =
                            Set<TournamentRules>.from(rulesFilter);
                        if (selected) {
                          newFilter.add(rules);
                        } else {
                          newFilter.remove(rules);
                        }
                        ref.read(rulesFilterProvider.notifier).state =
                            newFilter;
                        ref
                            .read(rulesFilterPrefProvider.notifier)
                            .set(newFilter);
                      },
                    ),
                ],
              ),
            ),
            tabs: [
              const Tab(text: 'Live'),
              const Tab(text: 'Upcoming'),
              const Tab(text: 'Past'),
              if (testMode) const Tab(text: 'Test'),
            ],
            children: [
              const TournamentList(when: WhenTournament.live),
              const TournamentList(when: WhenTournament.upcoming),
              const PastTournamentList(),
              if (testMode) const TournamentList(when: WhenTournament.test),
            ],
          );
        },
      ),
    );
  }

  static DateTime _lastTap = DateTime.now();
  static int _tapCount = 0;
}

class TournamentList extends ConsumerWidget {
  const TournamentList({required this.when, super.key});

  final WhenTournament when;

  Future<void> _handleTournamentSelection({
    required BuildContext context,
    required WidgetRef ref,
    required TournamentData tournament,
  }) async {
    // Unsubscribe from existing topics first
    final service = ref.read(notificationPreferencesProvider);
    await service.unsubscribeFromAllTopics();

    if (tournament.status != 'past') {
      if (!context.mounted) return;
      final choice = await showDialog<NotificationChoice>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: Text(tournament.name),
          content: const Text(
            'Would you like to receive notifications and alarms for this tournament?'
          ),
          actions: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  OutlinedButton(
                    onPressed: () => Navigator.pop(context, NotificationChoice.none),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('No Notifications'),
                    ),
                  ),
                  const SizedBox(height: 20),
                  FilledButton.tonal(
                    onPressed: () => Navigator.pop(context, NotificationChoice.updates),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('Score, schedule and seating update notifications only'),
                    ),
                  ),
                  const SizedBox(height: 20),
                  FilledButton(
                    onPressed: () => Navigator.pop(context, NotificationChoice.all),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('All the above notifications, plus an alarm at the start of each round'),
                    ),
                  ),
                  const SizedBox(height: 20),
                  FilledButton.tonal(
                    onPressed: () => Navigator.pop(context, NotificationChoice.alarmsOnly),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('Alarms at the start of each round, but no other notifications'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );

      // Handle the case where choice is null (dialog was dismissed)
      if (choice == null) return;

      await service.updatePreferences(choice);
    }

    // Set the tournament ID last to avoid race conditions
    await ref.read(tournamentIdProvider.notifier).set(tournament.id);

    if (!context.mounted) return;
    Navigator.of(context).pushReplacementNamed(ROUTES.tournament);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tournamentId = ref.watch(tournamentIdProvider);
    final tournamentList = ref.watch(tournamentListProvider(when));
    final rulesFilter = ref.watch(rulesFilterProvider);

    // Apply rules filter
    final filteredList = tournamentList.where((tournament) {
      return rulesFilter.isEmpty || rulesFilter.contains(tournament.rules);
    }).toList();

    if (filteredList.isEmpty) {
      return const Center(child: Text('No Tournaments Found'));
    }
    return ListView(
      padding: const EdgeInsets.all(8),
      children: [
        for (final tournament in filteredList)
          Card(
            child: ListTile(
              leading: switch (tournament.urlIcon) {
                "" => const Icon(Icons.event),
                _ => CachedNetworkImage(
                    height: 70,
                    width: 70,
                    imageUrl: tournament.urlIcon,
                    placeholder: (c, u) => const Center(
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
                  Text(tournament.rules.displayName),
                ],
              ),
              onTap: () => _handleTournamentSelection(
                context: context,
                ref: ref,
                tournament: tournament,
              ),
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
    final rulesFilter = ref.watch(rulesFilterProvider);

    return summaries.when(
      loading: () => const LoadingView(),
      error: (error, stack) => ErrorView(error: error, stackTrace: stack),
      data: (summaries) {
        final filteredSummaries = summaries.where((summary) {
          final rules = TournamentRules.fromString(summary.rules);
          return rulesFilter.isEmpty || rulesFilter.contains(rules);
        }).toList();

        if (filteredSummaries.isEmpty) {
          return const Center(child: Text('No Tournaments Found'));
        }

        return ListView.builder(
          itemCount: filteredSummaries.length,
          itemBuilder: (context, index) {
            final summary = filteredSummaries[index];
            return ListTile(
              title: Text(summary.name),
              subtitle: Text(
                '${DateFormat.yMMMd().format(summary.startDate)} - '
                '${DateFormat.yMMMd().format(summary.endDate)}\n'
                '${summary.venue}, ${summary.country}\n'
                '${summary.playerCount} players - ${TournamentRules.fromString(summary.rules).displayName}',
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
                  await ref
                      .read(pastTournamentDetailsProvider(summary.id).future);

                  // Set the tournament ID
                  await ref.read(tournamentIdProvider.notifier).set(summary.id);

                  // Navigate to tournament page
                  if (context.mounted) {
                    Navigator.pop(context); // Dismiss loading dialog
                    Navigator.of(context).pushReplacementNamed(ROUTES.tournament);
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
        );
      },
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
