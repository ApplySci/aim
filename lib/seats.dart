import 'package:flutter/material.dart';
import 'package:flutter_redux/flutter_redux.dart';
import 'store.dart';

class Seating extends StatelessWidget {
  const Seating({super.key});

  @override
  Widget build(BuildContext context) {
    return StoreConnector<AllState, Map<String, dynamic>>(
      converter: (store) {
        return {
          'seating': store.state.seating,
        };
      },
      builder: (BuildContext context, Map<String, dynamic> storeValues) {
        List seats = storeValues['seating'];
        return const Text('yo');
      },
    );
  }
}
