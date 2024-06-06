import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/views/schedule_list.dart';

class Seating extends ConsumerWidget {
  const Seating({super.key});

  @override
  Widget build(context, ref) {
    final showAll = ref.watch(showAllProvider);
    final filtered =
        ref.watch(filterByPlayerIdProvider.select((e) => e != null));
    return DefaultTabController(
      length: 2,
      child: Column(children: [
        const TabBar(tabs: [
          Tab(text: 'Upcoming'),
          Tab(text: 'Past'),
        ]),
        const Expanded(
          child: TabBarView(children: [
            ScheduleList(when: When.upcoming),
            ScheduleList(when: When.past),
          ]),
        ),
        if (filtered)
          SwitchListTile(
            title: const Text(
              'Show seating for all players',
              textAlign: TextAlign.right,
            ),
            value: showAll,
            onChanged: (value) => ref
                .read(showAllProvider.notifier) //
                .state = value,
          ),
      ]),
    );
  }
}
