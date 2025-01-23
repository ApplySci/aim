import 'package:flutter_riverpod/flutter_riverpod.dart';
import '/providers.dart';
import '/utils.dart';

/// Provider for tracking which tournament rules are currently selected in the filter.
/// An empty set means no filtering (show all rules).
final rulesFilterProvider = StateProvider<Set<TournamentRules>>((ref) {
  return ref.watch(rulesFilterPrefProvider);
});
