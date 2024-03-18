import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import 'frame.dart';
import 'store.dart';
import 'utils.dart';

class Players extends StatelessWidget {
  const Players({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(converter: (store) {
      return {'selected': store.state.selected, 'players': store.state.players};
    }, builder: (BuildContext context, Map<String, dynamic> incoming) {
      return Frame(
        context,
        Center(
          child: Column(
            children: <Widget>[
              const Text('Select which player you want to follow'),
              PlayerList(
                players: incoming['players'],
                selected: incoming['selected'],
              ),
            ],
          ),
        ),
      );
    });
  }
}

class PlayerList extends StatefulWidget {
  final List<Player> players;
  final int selected;

  const PlayerList(
      {super.key, this.players = const <Player>[], this.selected = -1});

  @override
  State<PlayerList> createState() => _PlayerListState();
}

class _PlayerListState extends State<PlayerList> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();

  @override
  Widget build(BuildContext context) {
    _focusNode.requestFocus();
    return TypeAheadField<Player>(
      controller: _controller,
      focusNode: _focusNode,
      hideOnEmpty: false,
      hideOnUnfocus: false,
      hideOnLoading: false,
      hideOnError: false,
      hideKeyboardOnDrag: false,
      hideOnSelect: false,
      hideWithKeyboard: false,
      itemBuilder: (context, player) => ListTile(
        title: Container(
          color: player.id == widget.selected ? selectedHighlight : null,
          child: Row(
            children: [
              Expanded(
                flex: 1,
                child: player.id < 0
                    ? Container()
                    : const Icon(
                        Icons.account_circle,
                        color: Colors.green,
                      ),
              ),
              Expanded(
                flex: 9,
                child: Text(
                  player.name,
                  style: TextStyle(
                      color:
                          player.id == widget.selected ? Colors.black : null),
                ),
              ),
            ],
          ),
        ),
      ),
      onSelected: (Player selection) async {
        _controller.clear();
        store.dispatch({
          'type': STORE.setPlayerId,
          'playerId': selection.id,
        });
        Navigator.pop(context);
        /* notify(
        '{selection.name} will be highlighted in seating & scores, and you will receive updates for them',
        );
         */
      },
      suggestionsCallback: (String needle) {
        List<Player> selected;
        if (needle == '') {
          selected = widget.players;
        } else {
          final lowerText = needle.toLowerCase();
          selected = widget.players.where((Player option) {
            return option.name.toLowerCase().contains(lowerText);
          }).toList();
        }
        if (selected.isNotEmpty && selected[0].id != -1) {
          selected.insert(0, Player(-1, '(none)'));
        }
        return selected;
      },
    );
  }
}
