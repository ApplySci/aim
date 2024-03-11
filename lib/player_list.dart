import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'store.dart';

class Players extends StatelessWidget {
  const Players({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, List<String>>(converter: (store) {
      return store.state.players;
    }, builder: (BuildContext context, List<String> players) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('Select which player you want to follow'),
            PlayerList(players: players),
          ],
        ),
      );
    });
  }
}


class PlayerList extends StatefulWidget {

  final List<String> players;

  const PlayerList({super.key, this.players=const <String>[]});

  @override
  State<PlayerList> createState() => _PlayerListState();
}

class _PlayerListState extends State<PlayerList> {

  List<String> haystack = [];
  List<String> lowerHaystack = [];

  @override
  void initState() {
    super.initState();
    print('inner');
    print(widget.players);
    haystack = List<String>.from(widget.players);
    haystack.sort();
    lowerHaystack = [for (var name in haystack) name.toLowerCase()];
  }

  @override
  Widget build(BuildContext context) {
    print(haystack);
    return Autocomplete<String>(
      optionsBuilder: (TextEditingValue textEditingValue) {
        if (textEditingValue.text == '') {
          return haystack;
        }
        final lowerText = textEditingValue.text.toLowerCase();
        return lowerHaystack.where((String option) {
          return option.contains(lowerText);
        });
      },
      onSelected: (String selection) {
        debugPrint('You just selected $selection');
      },
    );
  }
}
