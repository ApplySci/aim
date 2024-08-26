import 'package:flutter_riverpod/flutter_riverpod.dart';

import '/models.dart';
import 'firestore.dart';
import 'shared_preferences.dart';


final seatMapProvider = StreamProvider((ref) async* {
  final playerList = await ref.watch(playerListProvider.future);
  yield {
    for (final player in playerList) player.seat: player,
  };
});

final selectedSeatProvider = NotifierProvider<SelectedSeatNotifier, int?>(
      () => SelectedSeatNotifier(),
);

class SelectedSeatNotifier extends Notifier<int?> {
  @override
  int? build() {
    PlayerId? id = ref.watch(selectedPlayerIdProvider);
    AsyncValue<Map<PlayerId, PlayerData>> playerMapAsync = ref.watch(playerMapProvider);

    return playerMapAsync.when(
      data: (playerMap) => id != null ? playerMap[id]?.seat : null,
      loading: () => null,
      error: (_, __) => null,
    );
  }
}
