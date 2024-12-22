import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_html/flutter_html.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:timezone/timezone.dart' as tz;

import '/providers.dart';
import '/venue.dart';
import '/views/error_view.dart';
import '/views/loading_view.dart';
import '/views/utils.dart';

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
          Padding(
            padding: const EdgeInsets.all(8),
            child: Center(
              child: switch (tournament.urlIcon) {
                String url when url.isNotEmpty => CachedNetworkImage(
                    width: 128,
                    imageUrl: url,
                    placeholder: (context, url) => const CircularProgressIndicator(),
                    errorWidget: (context, url, error) => const Icon(
                      Icons.emoji_events,
                      size: 128,
                    ),
                    fadeInDuration: const Duration(milliseconds: 300),
                  ),
                _ => const Icon(
                    Icons.emoji_events,
                    size: 128,
                  ),
              },
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
              visualDensity: VisualDensity.compact,
            ),
            _ => ListTile(
                leading: const Text(""),
                title: Text(tournament.name),
                visualDensity: VisualDensity.compact,
            ),
          },
          ListTile(
            leading: const Icon(Icons.location_on),
            title: const Text('Location (tap for map)'),
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
           if (tournament.htmlnotes != null && tournament.htmlnotes!.isNotEmpty)
            ListTile(
              leading: const Icon(Icons.notes),
              title: const Text('Notes'),
              subtitle: Html(
                data: tournament.htmlnotes,
                style: {
                  "body": Style(
                    margin: Margins.zero,
                    padding: HtmlPaddings.zero,
                  ),
                },
                shrinkWrap: true,
              ),
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
    final localTimeZone = ref.watch(localLocationProvider);
    final useEventTimezone = ref.watch(timezonePrefProvider);

    return rounds.when(
      skipLoadingOnReload: true,
      loading: () => const LoadingView(),
      error: (error, stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
      data: (rounds) => localTimeZone.when(
        loading: () => const LoadingView(),
        error: (error, stackTrace) => ErrorView(
          error: error,
          stackTrace: stackTrace,
        ),
        data: (localTimeZone) => Padding(
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
              TableRow(children: [
                const Padding(
                  padding: EdgeInsets.all(8),
                  child: Text(
                    'Round',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Text.rich(
                    TextSpan(
                      children: [
                        const TextSpan(
                          text: 'Starts At',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        if (!useEventTimezone)
                          const TextSpan(text: ' (phone time)'),
                      ],
                    ),
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
                      '${DateFormat('EEEE d MMMM').format(schedule.start)}'
                      ' ${useEventTimezone
                        ? formatTimeWithDifference(schedule.start, localTimeZone)
                        : DateFormat('HH:mm').format(
                              tz.TZDateTime.from(schedule.start, localTimeZone)
                            )}',
                    ),
                  ),
                ]),
            ],
          ),
        ),
      ),
    );
  }
}
