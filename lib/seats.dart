import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'package:intl/intl.dart';

import 'store.dart';
import 'utils.dart';

typedef SeatingState = ({
  List<RoundState> theseSeats,
  List<RoundState> seating,
  int? selected,
  int roundDone,
  ScheduleState schedule
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
    return StoreConnector<AllState, SeatingState>(
      converter: (store) => (
        theseSeats: store.state.theseSeats,
        seating: store.state.seating,
        selected: store.state.selected,
        roundDone: store.state.roundDone,
        schedule: store.state.schedule!,
      ),
      builder: (context, state) {
        final haveSelection = state.selected != null;
        final seats =
            haveSelection && !showAll ? state.theseSeats : state.seating;
        if (seats.isEmpty) {
          return const Center(child: Text('No seating schedule available'));
        }

        return Column(
          children: [
            if (haveSelection)
              SwitchListTile(
                title: const Text('Selected Player / All Players'),
                value: showAll,
                onChanged: toggleShowAll,
              ),
            Expanded(
              child: ListView(
                children: [
                  for (final round in seats)
                    HanchanTable(
                      round: round,
                      schedule: state.schedule,
                      roundDone: state.roundDone,
                    ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

typedef AssignedTableState = ({
  int? selected,
  Map playerMap,
  bool japaneseWinds,
});

class AssignedTable extends StatelessWidget {
  const AssignedTable(
    this.seats, {
    super.key,
  });

  final List<int> seats; // E,S,N,W player indices

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, AssignedTableState>(
      converter: (store) => (
        selected: store.state.selected,
        playerMap: store.state.playerMap,
        japaneseWinds: prefs.getBool('japaneseWinds') ?? false,
      ),
      builder: (context, state) {
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
                  color: seats[wind.index] == state.selected
                      ? selectedHighlight
                      : Colors.transparent,
                ),
                children: [
                  //selected: seats[wind.index] == s.selected,
                  Padding(
                    padding: const EdgeInsets.all(8),
                    child: Text(
                      switch (state.japaneseWinds) {
                        true => wind.japanese,
                        false => wind.western,
                      },
                      textAlign: TextAlign.center,
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8),
                    child: Text(state.playerMap[seats[wind.index]]!),
                  ),
                ],
              ),
          ],
        );
      },
    );
  }
}

class HanchanTable extends StatelessWidget {
  const HanchanTable({
    super.key,
    required this.round,
    required this.schedule,
    required this.roundDone,
  });

  final RoundState round;
  final ScheduleState schedule;
  final int roundDone;

  @override
  Widget build(BuildContext context) {
    final roundName = schedule.hanchan[round.id]!.name;
    final startTime = DateFormat('EEEE d MMMM HH:mm')
        .format(schedule.hanchan[round.id]!.start);

    return Column(children: [
      Container(
        margin: const EdgeInsets.all(8.0),
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(
              width: 3,
              color: Colors.blueAccent,
            ),
          ),
        ),
      ),
      ListTile(
        leading: const Icon(Icons.watch_later_outlined),
        title: Text("$roundName begins at $startTime"),
      ),
      for (final MapEntry(:key, :value) in round.tables.entries)
        Column(children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.table_restaurant),
              Text(' $key'),
            ],
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: AssignedTable(value),
          ),
          const SizedBox(height: 10),
        ])
    ]);
  }
}
