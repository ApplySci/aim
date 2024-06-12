import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/providers.dart';
import '/views/schedule_list.dart';

class PlayerScheduleTab extends ConsumerWidget {
  const PlayerScheduleTab({
    required this.player,
    super.key,
  });

  final PlayerScore player;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ProviderScope(
      overrides: [
        showAllProvider.overrideWith((ref) => false),
        filterByPlayerIdProvider.overrideWith((ref) => player.id),
      ],
      child: const ScheduleList(when: When.all),
    );
  }
}
