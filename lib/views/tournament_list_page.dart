import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/utils.dart';
import '/views/error_view.dart';
import 'loading_view.dart';

class TournamentListPage extends ConsumerWidget {
  const TournamentListPage({super.key});

  @override
  Widget build(BuildContext context, ref) {
    final allTournamentsAsync = ref.watch(allTournamentsListProvider);
    return allTournamentsAsync.when(
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
            error: error,
            stackTrace: stackTrace,
          ),
      data: (_) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('Tournaments'),
          ),
          body: DefaultTabController(
            length: 3,
            child: Column(children: [
              Material(
                color: Theme
                    .of(context)
                    .colorScheme
                    .inversePrimary,
                child: const TabBar(tabs: [
                  Tab(text: 'Live'),
                  Tab(text: 'Upcoming'),
                  Tab(text: 'Past'),
                ]),
              ),
              const Expanded(
                child: TabBarView(children: [
                  TournamentList(when: WhenTournament.live),
                  TournamentList(when: WhenTournament.upcoming),
                  TournamentList(when: WhenTournament.past),
                ]),
              ),
            ]),
          ),
        );
      },
    );
  }
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
                String urlIcon =>
                    CachedNetworkImage(
                      height: 70,
                      width: 70,
                      imageUrl: urlIcon,
                      placeholder: (c, u) =>
                      const Center(
                        child: CircularProgressIndicator(),
                      ),
                      errorWidget: (c, u, e) => const Icon(Icons.error),
                      fit: BoxFit.contain,
                    ),
                _ => null,
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
