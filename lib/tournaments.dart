import 'package:flutter/material.dart';

import 'db.dart';
import 'store.dart';
import 'utils.dart';

class Tournaments extends StatelessWidget {
  const Tournaments({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Tournaments'),
      ),
      body: const TournamentList(),
    );
  }
}

class TournamentList extends StatefulWidget {
  const TournamentList({super.key});

  @override
  State<TournamentList> createState() => _TournamentListState();
}

class _TournamentListState extends State<TournamentList> {
  final tournament = DB.instance.getTournaments().map(
        (event) => event.docs.map(
          (e) => TournamentState.fromJson({
            'id': e.id,
            'address': '',
            ...(e.data() as Map).cast(),
          }),
        ),
      );

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: tournament,
      builder: (context, snapshot) {
        if (snapshot.error case Object error) {
          Log.error(error.toString());
          return const Text('Failed to get list of tournaments');
        } else if (snapshot.data case Iterable<TournamentState> data) {
          if (data.isEmpty) {
            return const Center(child: Text('No Tournaments Found'));
          }

          return ListView(
            padding: const EdgeInsets.all(8),
            children: data.map((t) {
              String dates = dateRange(
                t.startDate,
                t.endDate,
              );
              return Card(
                child: ListTile(
                  title: Text(t.name),
                  subtitle: Text("$dates\n${t.country}"),
                  onTap: () {
                    store.dispatch(SetTournamentAction(
                      tournament: t,
                    ));
                    Navigator.of(context).pushNamed(ROUTES.tournament);
                  },
                ),
              );
            }).toList(),
          );
        }
        return const Center(child: CircularProgressIndicator());
      },
    );
  }
}
