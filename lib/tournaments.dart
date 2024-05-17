import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';

import 'db.dart';
import 'fcm_client.dart';
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
      body: TournamentList(),
    );
  }
}

class TournamentList extends StatelessWidget {
  TournamentList({super.key});

  final Stream<QuerySnapshot> _tournaments = DB.instance.getTournaments();

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<QuerySnapshot>(
      stream: _tournaments,
      builder: (BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) {
        if (snapshot.hasError) {
          Log.error('snapshot failed to build tournament list');
          return const Text('Failed to get list of tournaments');
        }

        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Text("Now loading the list of tournaments");
        }
        return ListView(
          padding: const EdgeInsets.all(8),
          children: snapshot.data!.docs.map((DocumentSnapshot t) {
            final tData = TournamentState.fromJson({
              'id': t.id,
              'address': '',
              ...(t.data() as Map).cast(),
            });
            String dates = dateRange(
              tData.startDate,
              tData.endDate,
            );
            return Card(
              child: ListTile(
                title: Text(tData.name),
                subtitle: Text("$dates\n${tData.country}"),
                onTap: () {
                  subscribeToTopic(t.id, tData.id);
                  store.dispatch(SetTournamentAction(
                    tournament: tData,
                  ));
                  DB.instance.listenToTournament(t.id);
                  Navigator.pushNamed(context, ROUTES.tournament);
                },
              ),
            );
          }).toList(),
        );
      },
    );
  }
}
