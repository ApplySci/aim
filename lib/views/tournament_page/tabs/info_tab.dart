import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '/providers.dart';
import '/venue.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';

class TournamentInfo extends ConsumerWidget {
  const TournamentInfo({super.key});

  @override
  Widget build(context, ref) {
    final tournament = ref.watch(tournamentProvider);
    return tournament.when(
      skipLoadingOnReload: true,
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
      data: (tournament) => ListView(
        children: [
          if (tournament.urlIcon case String urlIcon)
            Padding(
              padding: const EdgeInsets.all(8),
              child: Center(
                child: CachedNetworkImage(
                  width: 128,
                  imageUrl: urlIcon,
                  placeholder: (context, url) =>
                      const CircularProgressIndicator(),
                  errorWidget: (context, url, error) => const Icon(Icons.error),
                ),
              ),
            ),
          switch (tournament.url) {
            String url => ListTile(
                leading: const Icon(Icons.public),
                title: Text(tournament.name),
                subtitle: Text(url),
                onTap: () => launchUrl(Uri.parse(url)),
                onLongPress: () async {
                  await Clipboard.setData(ClipboardData(text: url));

                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Copied url to clipboard')),
                  );
                },
              ),
            _ => ListTile(
                leading: const Icon(Icons.public),
                title: Text(tournament.name),
              ),
          },
          ListTile(
            leading: const Icon(Icons.location_on),
            title: const Text('Location'),
            subtitle: Text(tournament.address),
            onTap: () => openMap(context, tournament.address),
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
            title: const Text('Event Date'),
            subtitle: Text(tournament.when),
            visualDensity: VisualDensity.compact,
          ),
          const ListTile(
            leading: Icon(Icons.table_restaurant),
            title: Text('Hanchan Start Times'),
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
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
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
