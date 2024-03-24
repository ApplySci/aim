import 'package:cloud_firestore/cloud_firestore.dart';

import 'store.dart';
import 'utils.dart';

final _db = FirebaseFirestore.instance;

// Create a Reference to our pilot tournament file
//final cork2024 = _tournaments.child('Y3sDqxajiXefmP9XBTvY');
/*
    I think we're going to need scores, seats, players each in their own
    document, in a subcollection on the tournament, so that we can have separate
    listeners for each one

// const source = Source.cache; // Source can be CACHE, SERVER, or DEFAULT.


Future<void> getTournament() async {
  store.dispatch({'type': STORE.setPlayerList, 'players': cork2024.child('players')});
  store.dispatch({'type': STORE.setScores, 'players': cork2024.child('scores')});
  store.dispatch({'type': STORE.setSeating, 'players': cork2024.child('seating')});
}
 */

Stream<QuerySnapshot> getTournaments() {
  return _db.collection('tournaments').snapshots();
}

Future<dynamic> _downloadRef(ref) async {
  ref.get().then(
        (DocumentSnapshot doc) {
      final data = doc.data() as Map<String, dynamic>;
      // ...
    },
    onError: (e) => print("Error getting document: $e"),
  );
}

/*
https://github.com/firebase/quickstart-flutter/blob/main/firestore/lib/src/data/restaurant_provider.dart


/*
 *  Copyright 2022 Google LLC
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart' hide Filter;

abstract class RestaurantProvider {
  Stream<List<Restaurant>> get allRestaurants;
  void loadAllRestaurants();
  void loadFilteredRestaurants(model_filter.Filter filter);
  Future<Restaurant> getRestaurantById(String restaurantId);
  void dispose();
}

class FirestoreRestaurantProvider implements RestaurantProvider {
  FirestoreRestaurantProvider() {
    allRestaurants = _allRestaurantsController.stream;
  }

  final StreamController<List<Restaurant>> _allRestaurantsController =
      StreamController();

  @override
  late final Stream<List<Restaurant>> allRestaurants;

  @override
  void loadAllRestaurants() {
    final querySnapshot = FirebaseFirestore.instance
        .collection('restaurants')
        .orderBy('avgRating', descending: true)
        .limit(50)
        .snapshots();

    querySnapshot.listen((event) {
      final restaurants = event.docs.map((DocumentSnapshot doc) {
        return Restaurant.fromSnapshot(doc);
      }).toList();

      _allRestaurantsController.add(restaurants);
    });
  }

  @override
  void loadFilteredRestaurants(model_filter.Filter filter) {
    Query collection = FirebaseFirestore.instance.collection('restaurants');
    if (filter.category != null) {
      collection = collection.where('category', isEqualTo: filter.category);
    }
    if (filter.city != null) {
      collection = collection.where('city', isEqualTo: filter.city);
    }
    if (filter.price != null) {
      collection = collection.where('price', isEqualTo: filter.price);
    }
    final querySnapshot = collection
        .orderBy(filter.sort ?? 'avgRating', descending: true)
        .limit(50)
        .snapshots();

    querySnapshot.listen((event) {
      final restaurants = event.docs.map((DocumentSnapshot doc) {
        return Restaurant.fromSnapshot(doc);
      }).toList();

      _allRestaurantsController.add(restaurants);
    });
  }

  @override
  void dispose() {
    _allRestaurantsController.close();
  }

  @override
  Future<Restaurant> getRestaurantById(String restaurantId) {
    return FirebaseFirestore.instance
        .collection('restaurants')
        .doc(restaurantId)
        .get()
        .then((DocumentSnapshot doc) => Restaurant.fromSnapshot(doc));
  }

  Future<List<Review>> getReviewsForRestaurant(String restaurantId) {
    return FirebaseFirestore.instance
        .collection('restaurants')
        .doc(restaurantId)
        .collection('ratings')
        .get()
        .then((QuerySnapshot snapshot) {
      return snapshot.docs.map((DocumentSnapshot doc) {
        return Review.fromSnapshot(doc);
      }).toList();
    });
  }
}


https://github.com/firebase/quickstart-flutter/tree/main/firestore

final docRef = db.collection("cities").doc("SF");

'Downloaded ${ref.name} \n from bucket: ${ref.bucket}\n '
'at path: ${ref.fullPath} \n'
'Wrote "${ref.fullPath}" to tmp-${ref.name}',

https://firebase.google.com/docs/firestore/query-data/listen#dart

final listener = docRef.snapshots().listen(
      (event) => print("current data: ${event.data()}"),
      onError: (error) => print("Listen failed: $error"),
    );

...
listener.cancel();

*/
