import 'package:aim_tournaments/fcm_client.dart';
import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';

import 'db.dart';
import 'store.dart';
import 'utils.dart';

typedef PlayersState = ({
  List<Player> players,
  int? selected,
});

class Players extends StatefulWidget {
  const Players({super.key});

  @override
  State<Players> createState() => _PlayersState();
}

class _PlayersState extends State<Players> {
  final textController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, PlayersState>(
      distinct: true,
      converter: (store) => (
        players: store.state.players,
        selected: store.state.selected,
      ),
      builder: (context, state) {
        return Column(
          children: [
            Material(
              color: Theme.of(context).canvasColor,
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: textController,
                  decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: textController.text.isNotEmpty
                        ? IconButton(
                            onPressed: () =>
                                setState(() => textController.clear()),
                            icon: const Icon(Icons.clear),
                          )
                        : null,
                    hintText: 'Player search',
                  ),
                  onChanged: (value) => setState(() {}),
                ),
              ),
            ),
            Expanded(
              child: PlayerList(
                players: state.players
                    .where((e) => e.name
                        .toLowerCase()
                        .contains(textController.text.toLowerCase()))
                    .toList(),
                selected: state.selected,
              ),
            ),
          ],
        );
      },
    );
  }
}

class PlayerList extends StatelessWidget {
  const PlayerList({
    required this.players,
    required this.selected,
    super.key,
  });

  final List<Player> players;
  final int? selected;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: players.length,
      itemBuilder: (context, index) {
        final player = players[index];
        return ListTile(
          selected: player.id == selected,
          selectedColor: Theme.of(context).textTheme.titleMedium?.color,
          selectedTileColor: Theme.of(context).colorScheme.inversePrimary,
          leading: const Icon(
            Icons.account_circle,
            color: Colors.green,
          ),
          title: Text(player.name),
          onTap: () {
            if (player.id == selected) {
              store.dispatch(const SetPlayerIdAction(playerId: null));
              DB.instance.setAllAlarms();

              messaging.unsubscribeFromTopic(
                '${store.state.tournament?.id}-$selected',
              );
            } else {
              store.dispatch(SetPlayerIdAction(playerId: player.id));
              DB.instance.setAllAlarms();

              ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                content: Text(
                  '${player.name} will be highlighted in seating & scores, and you will receive updates for them',
                ),
              ));
              subscribeToTopic(
                '${store.state.tournament?.id}-${player.id}',
                '${store.state.tournament?.id}-$selected',
              );
            }
          },
        );
      },
    );
  }
}
