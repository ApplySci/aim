import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_sticky_header/flutter_sticky_header.dart';
import 'package:intl/intl.dart';

import '/models.dart';
import '/providers.dart';
import '/utils.dart';

typedef Round = ({
  String id,
  String name,
  DateTime start,
  List<RoundTable> tables,
});

typedef RoundTable = ({
  String name,
  Map<Wind, PlayerData> players,
});

extension on RoundTable {
  bool hasPlayerId(int? playerId) =>
      players.values.any((e) => e.id == playerId);
}

final showAllProvider = StateProvider((ref) => false);

final roundListProvider = StreamProvider((ref) async* {
  final schedule = await ref.watch(scheduleProvider.future);
  final roundList = await ref.watch(seatingProvider.future);
  final playerList = await ref.watch(playerListProvider.future);

  final playerById = Map.fromEntries(
    playerList.map((e) => MapEntry(e.id, e.name)),
  );
  yield [
    for (final (index, round) in roundList.indexed)
      (
        id: round.id,
        name: schedule.rounds[index].name,
        start: schedule.rounds[index].start,
        tables: [
          for (final MapEntry(key: tableName, value: playerIds)
              in round.tables.entries)
            (
              name: tableName,
              players: {
                for (final wind in Wind.values)
                  wind: PlayerData(
                    playerIds[wind.index],
                    playerById[playerIds[wind.index]]!,
                  ),
              },
            )
        ],
      ),
  ];
});

class Seating extends ConsumerWidget {
  const Seating({super.key});

  @override
  Widget build(context, ref) {
    final showAll = ref.watch(showAllProvider);
    final selectedPlayerId = ref.watch(selectedPlayerIdProvider);
    return DefaultTabController(
      length: 2,
      child: Column(children: [
        const TabBar(tabs: [
          Tab(text: 'Upcoming'),
          Tab(text: 'Past'),
        ]),
        const Expanded(
          child: TabBarView(children: [
            SeatingList(when: When.upcoming),
            SeatingList(when: When.past),
          ]),
        ),
        if (selectedPlayerId != null)
          SwitchListTile(
            title: const Text('All Players'),
            value: showAll,
            onChanged: (value) => ref
                .read(showAllProvider.notifier) //
                .state = value,
          ),
      ]),
    );
  }
}

enum When {
  upcoming,
  past,
}

final orderedRoundList = StreamProvider.family<Iterable<Round>, When>(
  (ref, when) async* {
    final roundList = await ref.watch(roundListProvider.future);
    yield switch (when) {
      When.upcoming => roundList,
      When.past => roundList.reversed,
    };
  },
);

final filteredRoundList = StreamProvider.family<Iterable<Round>, When>(
  (ref, when) async* {
    final now = DateTime.now();
    final roundList = await ref.watch(orderedRoundList(when).future);
    yield roundList.where((round) {
      return switch (when) {
        When.upcoming => round.start.isAfter(now),
        When.past => !round.start.isAfter(now),
      };
    });
  },
);

class SeatingList extends ConsumerWidget {
  const SeatingList({
    super.key,
    required this.when,
  });

  final When when;

  @override
  Widget build(context, ref) {
    final roundList = ref.watch(filteredRoundList(when));
    final selectedPlayerId = ref.watch(selectedPlayerIdProvider);
    final showAll = ref.watch(showAllProvider);

    return roundList.when(
      skipLoadingOnReload: true,
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => Center(child: Text('$error')),
      data: (roundList) {
        if (roundList.isEmpty) {
          return const Center(child: Text('No seating schedule available'));
        }
        return CustomScrollView(
          slivers: [
            for (final round in roundList)
              SliverStickyHeader(
                header: Material(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  elevation: 1,
                  child: ListTile(
                    leading: const Icon(Icons.watch_later_outlined),
                    title: Text(round.name),
                    subtitle: Text(
                      DateFormat('EEEE d MMMM HH:mm').format(round.start),
                    ),
                    visualDensity: VisualDensity.compact,
                  ),
                ),
                sliver: SliverPadding(
                  padding: const EdgeInsets.only(bottom: 16),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      for (final table in round.tables)
                        if (showAll ||
                            selectedPlayerId == null ||
                            table.hasPlayerId(selectedPlayerId))
                          Column(children: [
                            ListTile(
                              leading: const Icon(Icons.table_restaurant),
                              title: Text(table.name),
                            ),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 8),
                              child: AssignedTable(players: table.players),
                            ),
                          ]),
                    ]),
                  ),
                ),
              ),
          ],
        );
      },
    );
  }
}

class AssignedTable extends ConsumerWidget {
  const AssignedTable({
    required this.players,
    super.key,
  });

  final Map<Wind, PlayerData> players;

  void onTap(BuildContext context, int playerId) {}

  @override
  Widget build(context, ref) {
    final selectedPlayerId = ref.watch(selectedPlayerIdProvider);
    final japaneseWinds = ref.watch(japaneseWindsProvider);
    final playerWinds = Wind.values.map(
      (wind) => (wind: wind, player: players[wind]),
    );
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
        for (final (:wind, :player) in playerWinds)
          TableRow(
            decoration: BoxDecoration(
              color: player?.id == selectedPlayerId
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
              InkWell(
                onTap: player != null ? () => onTap(context, player.id) : null,
                child: Padding(
                  padding: const EdgeInsets.all(8),
                  child: Text(player?.name ?? ''),
                ),
              ),
            ],
          ),
      ],
    );
  }
}
