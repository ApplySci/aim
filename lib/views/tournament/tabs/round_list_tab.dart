import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/utils.dart';
import '/providers/firestore.dart';
import '/views/schedule_list.dart';
import '/views/tab_scaffold.dart';

class Seating extends ConsumerWidget {
  const Seating({super.key});

  @override
  Widget build(context, ref) {
    final showAll = ref.watch(showAllProvider);
    final filtered = ref.watch(filterByPlayerProvider.select((e) => e != null));
    final info = ref.watch(tournamentInfoProvider).valueOrNull;
    final status = info?.status ?? WhenTournament.upcoming;

    final Widget allToggle = SwitchListTile(
      title: const Text(
        'Show seating for all players',
        textAlign: TextAlign.right,
      ),
      value: showAll,
      onChanged: (value) => ref
          .read(showAllProvider.notifier)
          .state = value,
    );

    return(status == WhenTournament.live)
      ? TabScaffold(
          title: const Text('Seating'),
          tabs: const [
            Tab(text: 'Upcoming'),
            Tab(text: 'Past'),
          ],
          children: [
            const ScheduleList(when: When.upcoming),
            const ScheduleList(when: When.past),
          ],
        )
      : Column(children: [
          const Expanded(child: ScheduleList(when: When.all)),
          if (filtered) allToggle,
      ]);
  }
}
