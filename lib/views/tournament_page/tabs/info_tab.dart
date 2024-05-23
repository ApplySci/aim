import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '/providers.dart';
import '/venue.dart';

class TournamentInfo extends ConsumerWidget {
  const TournamentInfo({super.key});

  @override
  Widget build(context, ref) {
    final tournament = ref.watch(tournamentProvider);
    return tournament.when(
      skipLoadingOnReload: true,
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => Center(child: Text('$error')),
      data: (tournament) => ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.location_on),
            title: Text(tournament.address),
            trailing: IconButton(
              onPressed: () => openMap(context, tournament.address),
              icon: const Icon(Icons.open_in_new),
            ),
            onLongPress: () async {
              await Clipboard.setData(ClipboardData(text: tournament.address));

              if (!context.mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Copied address to clipboard')),
              );
            },
            visualDensity: VisualDensity.compact,
          ),
          ListTile(
            leading: const Icon(Icons.calendar_month),
            title: Text(tournament.when),
            visualDensity: VisualDensity.compact,
          ),
          const ListTile(
            leading: Icon(Icons.table_restaurant),
            title: Text('Hanchan timings'),
            visualDensity: VisualDensity.compact,
          ),
          const ScheduleTable(),
        ],
      ),
    );
  }
}

class ScheduleTable extends ConsumerWidget {
  const ScheduleTable({super.key});

  @override
  Widget build(context, ref) {
    final rounds = ref.watch(scheduleProvider.selectAsyncData(
      (schedule) => schedule.rounds,
    ));
    return rounds.when(
      skipLoadingOnReload: true,
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => ListTile(title: Text('$error')),
      data: (rounds) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8),
        child: Table(
          border: TableBorder.all(
            width: 2,
            color: const Color(0x88888888),
          ),
          columnWidths: const {
            0: IntrinsicColumnWidth(),
            1: FlexColumnWidth(),
          },
          children: [
            const TableRow(children: [
              Padding(
                padding: EdgeInsets.all(8),
                child: Text(
                  'Round',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              Padding(
                padding: EdgeInsets.all(8),
                child: Text(
                  'Starts At',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ]),
            for (final schedule in rounds)
              TableRow(children: [
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Text(schedule.name),
                ),
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Text(
                      DateFormat('EEEE d MMMM HH:mm').format(schedule.start)),
                ),
              ]),
          ],
        ),
      ),
    );
  }
}
