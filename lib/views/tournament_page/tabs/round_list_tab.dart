import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/utils.dart';
import '/providers/firestore.dart';
import '/views/schedule_list.dart';

class Seating extends ConsumerWidget {
  const Seating({super.key});

  @override
  Widget build(context, ref) {
    final showAll = ref.watch(showAllProvider);
    final filtered = ref.watch(filterByPlayerProvider.select((e) => e != null));
    final tournamentStatus = ref.watch(tournamentStatusProvider);

    final Widget allToggle = SwitchListTile(
      title: const Text(
        'Show seating for all players',
        textAlign: TextAlign.right,
      ),
      value: showAll,
      onChanged: (value) => ref
          .read(showAllProvider.notifier) //
          .state = value,
    );

    // TODO if there are no upcoming rounds, only show the past tab, & vice versa
    return(tournamentStatus == WhenTournament.live)
      ? DefaultTabController(
          length: 2,
          child: Column(children: [
            Material(
              color: Theme.of(context).colorScheme.inversePrimary,
              child: const TabBar(tabs: [
                Tab(text: 'Upcoming'),
                Tab(text: 'Past'),
              ]),
            ),
            const Expanded(
              child: TabBarView(children: [
                ScheduleList(when: When.upcoming),
                ScheduleList(when: When.past),
              ]),
            ),
            if (filtered) allToggle,
          ]),
        )
      : Column(children: [
          const Expanded(child: ScheduleList(when: When.all)),
          if (filtered) allToggle,
      ]);
  }
}
