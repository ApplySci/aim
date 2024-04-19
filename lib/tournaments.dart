import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'db.dart';
import 'fcm_client.dart';
import 'frame.dart';
import 'store.dart';
import 'utils.dart';

class Tournaments extends StatelessWidget {
  const Tournaments({super.key});

  @override
  Widget build(BuildContext context) {
    return Frame(
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
                Map<String, dynamic> metadata =
                    t.data()! as Map<String, dynamic>;
                // TODO make it a function that returns a string with nice format
                DateTime sd = metadata['start_date'].toDate();
                DateTime ed = metadata['end_date'].toDate();
                String dateRange = 'ERROR: unassigned dateRange!';
                if (sd.year == ed.year) {
                  if (sd.month == ed.month && sd.day == ed.day) {
                    dateRange = DateFormat('HH:mm').format(sd);
                  } else {
                    dateRange = DateFormat('HH:mm d MMM').format(sd);
                  }
                } else {
                  dateRange = DateFormat('HH:mm d MMM y').format(sd);
                }
                return ListTile(
                  title: Text(metadata['name']),
                  subtitle: Text(
                      "$dateRange - ${DateFormat('HH:mm d MMM y').format(ed)}"
                      "\n${metadata['country']}"),
                  onTap: () {
                    subscribeUserToTopic(t.id, store.state.tournament);
                    DB.instance.getTournament(t);
                    Navigator.popAndPushNamed(context, ROUTES.scoreTable);
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
