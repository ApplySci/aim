import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'db.dart';
import 'fcm_client.dart';
import 'frame.dart';
import 'store.dart';
import 'utils.dart';

class Tournaments extends StatelessWidget {
  const Tournaments({super.key});

  @override
  Widget build(BuildContext context) {
    return navFrame(
      context,
      const Center(
        child: Column(
          children: <Widget>[
            Text('Pick a tournament to follow'),
            TournamentList(),
          ],
        ),
      ),
    );
  }
}

class TournamentList extends StatefulWidget {
  const TournamentList({super.key});

  @override
  State createState() => _TournamentListState();
}

class _TournamentListState extends State<TournamentList> {
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
          shrinkWrap: true,
          children: snapshot.data!.docs
              .map((DocumentSnapshot t) {
                Map<String, dynamic> tData = t.data()! as Map<String, dynamic>;
                String dates = dateRange(
                  tData['start_date'],
                  tData['end_date'],
                );
                return ListTile(
                  title: Text(tData['name']),
                  subtitle: Text("$dates\n${tData['country']}"),
                  onTap: () {
                    if (store.state.tournament['id'] != null
                    && t.id != store.state.tournament['id']) {
                      /*
                      unsubscribeFromTournament(store.state.tournament['id'],
                        store.state.players.length,
                      );
                       */
                      store.dispatch({
                        'type': STORE.setPlayerId,
                        'playerId': -2,
                      });
                    }
                    subscribeToTopic(t.id, store.state.tournament['id']);
                    store.dispatch({
                      'type': STORE.setTournament,
                      'tournamentId': t.id,
                      'tournament': tData,
                    });
                    DB.instance.listenToTournament(t.id);
                    Navigator.popAndPushNamed(context, ROUTES.info);
                  },
                );
              })
              .toList()
              .cast(),
        );
      },
    );
  }
}
