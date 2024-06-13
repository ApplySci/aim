import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/utils.dart';
import '/views/error_view.dart';
import 'loading_view.dart';

class TournamentListPage extends StatelessWidget {
  const TournamentListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tournaments'),
      ),
      body: const TournamentList(),
    );
  }
}

class TournamentList extends ConsumerWidget {
  const TournamentList({super.key});
  @override
  Widget build(context, ref) {
    final tournamentId = ref.watch(tournamentIdProvider);
    final tournamentList = ref.watch(tournamentListProvider);
    return tournamentList.when(
      skipLoadingOnReload: true,
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
      data: (tournamentList) {
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
                    String urlIcon => CachedNetworkImage(
                        height: 70,
                        width: 70,
                        imageUrl: urlIcon,
                        placeholder: (c, u) => const Center(
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
      },
    );
  }
}
