import 'package:collection/collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/utils.dart';

final searchProvider = StateProvider((_) => '');

final searchPlayerList = StreamProvider((ref) async* {
  final search = ref.watch(searchProvider);
  final playerList = await ref.watch(playerScoreListProvider.future);
  yield playerList
      .where(
        (player) => player.name.toLowerCase().contains(search),
      )
      .toList()
      .sortedBy((player) => player.name);
});

class Players extends ConsumerStatefulWidget {
  const Players({super.key});

  @override
  ConsumerState<Players> createState() => _PlayersState();
}

class _PlayersState extends ConsumerState<Players> {
  final textController = TextEditingController();

  @override
  void dispose() {
    textController.dispose();
    super.dispose();
  }

  @override
  Widget build(context) {
    final isSearching = ref.watch(
      searchProvider.select((search) => search.isNotEmpty),
    );
    return Column(
      children: [
        Material(
          color: Theme.of(context).canvasColor,
          child: Padding(
            padding: const EdgeInsets.all(8),
            child: TextFormField(
              controller: textController,
              decoration: InputDecoration(
                prefixIcon: const Icon(Icons.search),
                suffixIcon: isSearching
                    ? IconButton(
                        onPressed: () => textController.clear(),
                        icon: const Icon(Icons.clear),
                      )
                    : null,
                hintText: 'Player search',
              ),
              onChanged: (value) => ref
                  .read(searchProvider.notifier) //
                  .state = value.toLowerCase(),
            ),
          ),
        ),
        const Expanded(child: PlayerList()),
      ],
    );
  }
}

class PlayerList extends ConsumerWidget {
  const PlayerList({
    super.key,
  });

  @override
  Widget build(context, ref) {
    final playerList = ref.watch(searchPlayerList);
    return playerList.when(
      skipLoadingOnReload: true,
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => Center(child: Text('$error')),
      data: (playerList) => ListView.builder(
        itemCount: playerList.length,
        itemBuilder: (context, index) => PlayerTile(player: playerList[index]),
      ),
    );
  }
}

class PlayerTile extends ConsumerWidget {
  const PlayerTile({
    super.key,
    required this.player,
  });

  final PlayerScore player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isSelected = ref.watch(
      selectedPlayerIdProvider.select((id) => id == player.id),
    );
    return ListTile(
      selected: isSelected,
      selectedColor: Theme.of(context).textTheme.titleMedium?.color,
      selectedTileColor: Theme.of(context).colorScheme.inversePrimary,
      leading: const Icon(
        Icons.account_circle,
        color: Colors.green,
      ),
      title: Text(player.name),
      subtitle: Text('Rank: ${player.rank}'),
      trailing: IconButton(
        onPressed: () {
          final selectedPlayerIdNotifier =
              ref.read(selectedPlayerIdProvider.notifier);
          if (isSelected) {
            selectedPlayerIdNotifier.set(null);
          } else {
            selectedPlayerIdNotifier.set(player.id);
          }
        },
        icon: isSelected
            ? const Icon(Icons.favorite)
            : const Icon(Icons.favorite_border),
      ),
      onTap: () =>
          Navigator.of(context).pushNamed(ROUTES.player, arguments: player.id),
    );
  }
}
