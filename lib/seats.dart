import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'package:flutter_sticky_header/flutter_sticky_header.dart';
import 'package:intl/intl.dart';

import 'store.dart';
import 'utils.dart';

typedef Round = ({
  String id,
  String name,
  DateTime start,
  List<RoundTable> tables,
});

typedef RoundTable = ({
  String name,
  Map<Winds, Player> players,
});

extension on RoundTable {
  bool hasPlayerId(int? playerId) =>
      players.values.any((e) => e.id == playerId);
}

List<Round> toRoundList(
  List<RoundState> rounds,
  ScheduleState schedule,
  List<Player> players,
) {
  final playerById = Map.fromEntries(
    players.map((e) => MapEntry(e.id, e.name)),
  );
  final roundById = schedule.rounds;
  return [
    for (final round in rounds)
      (
        id: round.id,
        name: roundById[round.id]!.name,
        start: roundById[round.id]!.start,
        tables: [
          for (final MapEntry(key: tableName, value: playerIds)
              in round.tables.entries)
            (
              name: tableName,
              players: {
                for (final wind in Winds.values)
                  wind: Player(
                    playerIds[wind.index],
                    playerById[playerIds[wind.index]]!,
                  ),
              },
            )
        ],
      ),
  ];
}

typedef SeatingState = ({
  List<Round> rounds,
  int? selected,
  int roundDone,
  bool japaneseWinds,
});

class Seating extends StatefulWidget {
  const Seating({super.key});

  @override
  State<Seating> createState() => _SeatingState();
}

class _SeatingState extends State<Seating> {
  bool showAll = false;

  void toggleShowAll(bool yes) => setState(() => showAll = yes);

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, SeatingState?>(
      distinct: true,
      converter: (store) => store.state.schedule != null
          ? (
              rounds: toRoundList(
                store.state.seating,
                store.state.schedule!,
                store.state.players,
              ),
              selected: store.state.selected,
              roundDone: store.state.roundDone,
              japaneseWinds: prefs.getBool('japaneseWinds') ?? false,
            )
          : null,
      builder: (context, state) {
        if (state == null) {
          return const Center(child: CircularProgressIndicator());
        }

        return DefaultTabController(
          length: 2,
          child: Column(children: [
            const TabBar(tabs: [
              Tab(text: 'Upcoming'),
              Tab(text: 'Past'),
            ]),
            Expanded(
              child: TabBarView(children: [
                SeatingList(
                  when: When.upcoming,
                  state: state,
                  showAll: showAll,
                ),
                SeatingList(
                  when: When.past,
                  state: state,
                  showAll: showAll,
                ),
              ]),
            ),
            if (state.selected != null)
              SwitchListTile(
                title: const Text('Selected Player / All Players'),
                value: showAll,
                onChanged: toggleShowAll,
              ),
          ]),
        );
      },
    );
  }
}

enum When {
  upcoming,
  past,
}

class SeatingList extends StatelessWidget {
  const SeatingList({
    super.key,
    required this.when,
    required this.state,
    required this.showAll,
  });

  final When when;
  final SeatingState state;
  final bool showAll;

  Iterable<Round> get seats {
    final now = DateTime.now();
    return state.rounds.where((round) {
      return switch (when) {
        When.upcoming => round.start.isAfter(now),
        When.past => !round.start.isAfter(now),
      };
    });
  }

  @override
  Widget build(BuildContext context) {
    final seats = switch (when) {
      When.upcoming => this.seats,
      When.past => this.seats.toList().reversed,
    };
    if (seats.isEmpty) {
      return const Center(child: Text('No seating schedule available'));
    }

    return CustomScrollView(
      slivers: [
        for (final round in seats)
          SliverStickyHeader(
            header: Material(
              color: Theme.of(context).cardColor,
              elevation: 1,
              child: ListTile(
                leading: const Icon(Icons.watch_later_outlined),
                title: Text(round.name),
                subtitle:
                    Text(DateFormat('EEEE d MMMM HH:mm').format(round.start)),
                visualDensity: VisualDensity.compact,
              ),
            ),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                for (final table in round.tables)
                  if (showAll ||
                      state.selected == null ||
                      table.hasPlayerId(state.selected))
                    Column(children: [
                      ListTile(
                        leading: const Icon(Icons.table_restaurant),
                        title: Text(table.name),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        child: AssignedTable(
                          players: table.players,
                          selected: state.selected,
                          japaneseWinds: state.japaneseWinds,
                        ),
                      ),
                    ]),
              ]),
            ),
          ),
      ],
    );
  }
}

typedef AssignedTableState = ({
  int? selected,
  List<Player> players,
  bool japaneseWinds,
});

class AssignedTable extends StatelessWidget {
  const AssignedTable({
    required this.players,
    this.selected,
    required this.japaneseWinds,
    super.key,
  });

  final Map<Winds, Player> players;
  final int? selected;
  final bool japaneseWinds;

  @override
  Widget build(BuildContext context) {
    return Table(
      border: TableBorder.all(
        width: 2,
        color: const Color(0x88888888),
      ),
      columnWidths: const {
        0: IntrinsicColumnWidth(),
        1: FlexColumnWidth(),
      },
      children: [
        for (final wind in Winds.values)
          TableRow(
            decoration: BoxDecoration(
              color: players[wind]?.id == selected
                  ? selectedHighlight
                  : Colors.transparent,
            ),
            children: [
              Padding(
                padding: const EdgeInsets.all(8),
                child: Text(
                  switch (japaneseWinds) {
                    true => wind.japanese,
                    false => wind.western,
                  },
                  textAlign: TextAlign.center,
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8),
                child: Text(players[wind]!.name),
              ),
            ],
          ),
      ],
    );
  }
}
