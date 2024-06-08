import 'package:collection/collection.dart';
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

final showAllProvider = StateProvider((ref) => false);

final filterByPlayerIdProvider = Provider((ref) {
  return ref.watch(selectedPlayerIdProvider);
});

final filterByPlayerProvider = Provider((ref) {
  final playerId = ref.watch(filterByPlayerIdProvider);
  final playerList = ref.watch(playerListProvider);
  return playerList.value?.firstWhereOrNull((e) => e.id == playerId);
}, dependencies: [
  filterByPlayerIdProvider,
  playerListProvider,
]);

final roundListProvider = StreamProvider((ref) async* {
  final showAll = ref.watch(showAllProvider);
  final filterByPlayer = ref.watch(filterByPlayerProvider);
  final roundById = await ref.watch(scheduleProvider.selectAsync(
    (schedule) => Map.fromEntries(
      (schedule.rounds.map((e) => MapEntry(e.id, e))),
    ),
  ));
  final playerById = await ref.watch(playerListProvider.selectAsync(
    (playerList) => Map.fromEntries(
      playerList.map((e) => MapEntry(e.id, e.name)),
    ),
  ));

  final roundList = await ref.watch(seatingProvider.future);
  yield roundList
      .map(
        (round) => (
          id: round.id,
          name: roundById[round.id]!.name,
          start: roundById[round.id]!.start,
          tables: [
            for (final MapEntry(key: tableName, value: playerIds)
                in round.tables.entries)
              if (showAll ||
                  filterByPlayer == null ||
                  playerIds.contains(filterByPlayer.id))
                (
                  name: tableName,
                  players: {
                    for (final wind in Wind.values)
                      wind: PlayerData({
                        'id': playerIds[wind.index],
                        'name': playerById[playerIds[wind.index]]!,
                      }),
                  },
                )
          ],
        ),
      )
      .sortedBy((round) => round.start);
}, dependencies: [
  showAllProvider,
  filterByPlayerProvider,
]);

enum When {
  all,
  upcoming,
  past,
}

final orderedRoundList =
    StreamProvider.family<Iterable<Round>, When>((ref, when) async* {
  final roundList = await ref.watch(roundListProvider.future);
  yield switch (when) {
    When.all => roundList,
    When.upcoming => roundList,
    When.past => roundList.reversed,
  };
}, dependencies: [
  roundListProvider,
]);

final filteredRoundList = StreamProvider.family<Iterable<Round>, When>(
  (ref, when) async* {
    final now = DateTime.now();
    final roundList = await ref.watch(orderedRoundList(when).future);
    yield roundList.where((round) {
      return switch (when) {
        When.all => true,
        When.upcoming => round.start.isAfter(now),
        When.past => !round.start.isAfter(now),
      };
    });
  },
  dependencies: [
    orderedRoundList,
  ],
);

class ScheduleList extends ConsumerWidget {
  const ScheduleList({
    super.key,
    required this.when,
  });

  final When when;

  @override
  Widget build(context, ref) {
    final roundList = ref.watch(filteredRoundList(when));
    return roundList.when(
      skipLoadingOnReload: true,
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) =>
          ErrorScreen(error: error, stackTrace: stackTrace),
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
                        Column(children: [
                          ListTile(
                            leading: const Icon(Icons.table_restaurant),
                            title: Text(table.name),
                          ),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 8),
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

  void onTap(BuildContext context, PlayerId playerId) =>
      Navigator.of(context).pushNamed(ROUTES.player, arguments: playerId);

  @override
  Widget build(context, ref) {
    final filterByPlayerId = ref.watch(filterByPlayerIdProvider);
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
              color: player?.id == filterByPlayerId
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
