import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;

import 'package:alarm/alarm.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/timezone.dart';

import '/firebase_options.dart';
import '/models.dart';
import '/providers.dart';
import '/utils.dart';

/// Service for managing alarms both in foreground and background contexts
class AlarmService {
  // Prevent instantiation
  AlarmService._();

  /// Updates alarms based on current schedule data
  /// Works in both foreground (with providers) and background (direct Firebase calls)
  static Future<void> updateAlarms({
    dynamic ref,
    String? tournamentId,
    bool forceUpdate = false,
  }) async {
    try {
      Log.debug('Starting alarm update process');
      
      // Check if alarms are enabled
      final prefs = await SharedPreferences.getInstance();
      final alarmsEnabled = prefs.getBool('alarm') ?? true;
      
      Log.debug('Alarm preferences check: alarmsEnabled = $alarmsEnabled');
      
      if (!alarmsEnabled) {
        Log.debug('Alarms disabled, clearing all alarms');
        await Alarm.stopAll();
        return;
      }

      Log.debug('Calculating alarm schedule...');
      // Calculate new alarm schedule
      final alarmInfos = await _calculateAlarmSchedule(
        ref: ref,
        tournamentId: tournamentId,
        prefs: prefs,
      );

      Log.debug('Calculated ${alarmInfos.length} alarm(s)');
      for (int i = 0; i < alarmInfos.length; i++) {
        final alarm = alarmInfos[i];
        Log.debug('  Alarm $i: ${alarm.name} at ${alarm.alarm.toIso8601String()}');
      }

      if (alarmInfos.isEmpty) {
        Log.debug('No alarms to set, clearing all alarms');
        await Alarm.stopAll();
        return;
      }

      // Check if alarms are identical to current ones (skip if not forced)
      Log.debug('Checking if alarms are identical (forceUpdate: $forceUpdate)');
      if (!forceUpdate && await _areAlarmsIdentical(alarmInfos)) {
        Log.debug('Alarm schedule unchanged, skipping update');
        return;
      }

      Log.debug('Proceeding with alarm system update');
      // Update system alarms
      await _updateSystemAlarms(alarmInfos, ref: ref);
      
      Log.debug('Storing current alarm state');
      // Store current alarm state for comparison
      await _storeCurrentAlarmState(alarmInfos, prefs);
      
      Log.debug('Alarm update completed successfully');
    } catch (e, stack) {
      Log.error('Error updating alarms: $e');
      Log.debug('Stack trace: $stack');
    }
  }

  /// Calculates the alarm schedule based on current tournament data
  static Future<List<AlarmInfo>> _calculateAlarmSchedule({
    dynamic ref,
    String? tournamentId,
    required SharedPreferences prefs,
  }) async {
    try {
      Log.debug('_calculateAlarmSchedule START');
      
      // Get tournament ID
      final tId = tournamentId ?? prefs.getString('tournamentId');
      Log.debug('Using tournament ID: $tId');
      
      if (tId == null) {
        Log.debug('No tournament ID available');
        return [];
      }

      // Get player preference
      Log.debug('Getting player preferences...');
      final selectedPlayerData = prefs.getString('selectedPlayer');
      PlayerData? selectedPlayer;
      if (selectedPlayerData != null) {
        Log.debug('Found player data in preferences');
        final playerMap = jsonDecode(selectedPlayerData) as Map<String, dynamic>;
        final playerId = playerMap[tId] as String?;
        Log.debug('Player ID for tournament $tId: $playerId');
        
        if (playerId != null) {
          Log.debug('Fetching player data for: $playerId');
          selectedPlayer = await _getPlayerData(tId, playerId, ref: ref);
          Log.debug('Player data result: ${selectedPlayer?.name ?? "null"}');
        }
      } else {
        Log.debug('No player data in preferences');
      }

      // Get tournament data
      Log.debug('Fetching tournament data...');
      final tournamentData = await _getTournamentData(tId, ref: ref);
      if (tournamentData == null) {
        Log.debug('No tournament data available');
        return [];
      }
      Log.debug('Tournament data fetched: ${tournamentData.name}');

      // Get schedule and seating data
      Log.debug('Fetching schedule data...');
      final scheduleData = await _getScheduleData(tId, ref: ref);
      Log.debug('Schedule data result: ${scheduleData?.rounds.length ?? 0} rounds');
      
      Log.debug('Fetching seating data...');
      final seatingData = await _getSeatingData(tId, ref: ref);
      Log.debug('Seating data result: ${seatingData?.length ?? 0} rounds');
      
      if (scheduleData == null || seatingData == null) {
        Log.debug('No schedule or seating data available');
        return [];
      }

      // Get timezone
      Log.debug('Getting timezone...');
      final location = await _getTimezone(scheduleData, ref: ref);
      Log.debug('Using timezone: ${location.name}');
      
      // Get vibration preference
      final vibratePref = prefs.getBool('vibrate') ?? true;
      Log.debug('Vibration preference: $vibratePref');

      // Calculate alarms
      Log.debug('Building alarm list...');
      final alarms = <AlarmInfo>[];
      for (final round in seatingData) {
        Log.debug('Processing round: ${round.id}');
        final scheduleRound = scheduleData.rounds.where((r) => r.id == round.id).firstOrNull;
        if (scheduleRound != null) {
          Log.debug('Found schedule for round ${round.id}: ${scheduleRound.start}');
          final alarmTime = TZDateTime.from(
            scheduleRound.start,
            location,
          ).subtract(const Duration(minutes: 5));

          Log.debug('Alarm time calculated: ${alarmTime.toIso8601String()}');

          alarms.add((
            id: round.id,
            name: scheduleRound.name,
            alarm: alarmTime,
            vibratePref: vibratePref,
            player: selectedPlayer != null
                ? (
                    id: selectedPlayer.id,
                    name: selectedPlayer.name,
                    table: round.tableNameForSeat(selectedPlayer.seat),
                  )
                : null,
          ));
        } else {
          Log.debug('No schedule found for round: ${round.id}');
        }
      }

      Log.debug('_calculateAlarmSchedule END - ${alarms.length} alarms calculated');
      return alarms;
    } catch (e, stack) {
      Log.error('Error calculating alarm schedule: $e');
      Log.debug('Stack trace: $stack');
      return [];
    }
  }

  /// Gets tournament data either from providers or direct Firebase call
  static Future<TournamentData?> _getTournamentData(String tournamentId, {dynamic ref}) async {
    if (ref != null) {
      // Use provider if available
      try {
        final tournament = ref.read(tournamentProvider);
        return tournament.valueOrNull;
      } catch (e) {
        Log.debug('Error reading tournament from provider: $e');
      }
    }

    // Direct Firebase call
    try {
      await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
      final doc = await FirebaseFirestore.instance
          .collection('tournaments')
          .doc(tournamentId)
          .get();

      if (doc.exists) {
        return TournamentData.fromMap({
          'id': doc.id,
          'address': '',
          ...(doc.data() as Map).cast(),
        });
      }
    } catch (e) {
      Log.debug('Error getting tournament data from Firebase: $e');
    }

    return null;
  }

  /// Gets schedule data either from providers or direct Firebase call
  static Future<ScheduleData?> _getScheduleData(String tournamentId, {dynamic ref}) async {
    if (ref != null) {
      // Use provider if available
      try {
        final schedule = ref.read(scheduleProvider);
        return schedule.valueOrNull;
      } catch (e) {
        Log.debug('Error reading schedule from provider: $e');
      }
    }

    // Direct Firebase call
    try {
      await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
      final doc = await FirebaseFirestore.instance
          .collection('tournaments')
          .doc(tournamentId)
          .collection('v3')
          .doc('seating')
          .get();

      if (doc.exists) {
        final data = doc.data() ?? {};
        if (data.containsKey('timezone') && data.containsKey('rounds')) {
          return ScheduleData.fromSeating(data);
        }
      }
    } catch (e) {
      Log.debug('Error getting schedule data from Firebase: $e');
    }

    return null;
  }

  /// Gets seating data either from providers or direct Firebase call
  static Future<List<RoundData>?> _getSeatingData(String tournamentId, {dynamic ref}) async {
    if (ref != null) {
      // Use provider if available
      try {
        final seating = ref.read(seatingProvider);
        return seating.valueOrNull;
      } catch (e) {
        Log.debug('Error reading seating from provider: $e');
      }
    }

    // Direct Firebase call
    try {
      await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
      final doc = await FirebaseFirestore.instance
          .collection('tournaments')
          .doc(tournamentId)
          .collection('v3')
          .doc('seating')
          .get();

      if (doc.exists) {
        final data = doc.data() ?? {};
        if (data.containsKey('rounds')) {
          final location = getLocation(data['timezone'].toString());
          return [
            for (final Map round in data['rounds'])
              RoundData.fromMap(round.cast(), location),
          ];
        }
      }
    } catch (e) {
      Log.debug('Error getting seating data from Firebase: $e');
    }

    return null;
  }

  /// Gets player data either from providers or direct Firebase call
  static Future<PlayerData?> _getPlayerData(String tournamentId, String playerId, {dynamic ref}) async {
    if (ref != null) {
      // Use provider if available
      try {
        final playerMap = ref.read(playerMapProvider);
        return playerMap.valueOrNull?[playerId];
      } catch (e) {
        Log.debug('Error reading player from provider: $e');
      }
    }

    // Direct Firebase call
    try {
      await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
      final doc = await FirebaseFirestore.instance
          .collection('tournaments')
          .doc(tournamentId)
          .collection('v3')
          .doc('players')
          .get();

      if (doc.exists) {
        final data = doc.data() ?? {};
        if (data.containsKey('players')) {
          final players = [
            for (final Map<String, dynamic> player in data['players'])
              PlayerData(player.cast())
          ];
          return players.where((p) => p.id == playerId).firstOrNull;
        }
      }
    } catch (e) {
      Log.debug('Error getting player data from Firebase: $e');
    }

    return null;
  }

  /// Gets timezone either from providers or direct calculation
  static Future<Location> _getTimezone(ScheduleData scheduleData, {dynamic ref}) async {
    if (ref != null) {
      // Use provider if available
      try {
        final location = ref.read(locationProvider);
        return location.valueOrNull ?? UTC;
      } catch (e) {
        Log.debug('Error reading location from provider: $e');
      }
    }

    // Use tournament timezone or local timezone
    try {
      final localTimezone = await FlutterTimezone.getLocalTimezone();
      return getLocation(localTimezone);
    } catch (e) {
      Log.debug('Error getting timezone: $e');
      return UTC;
    }
  }

  /// Checks if the new alarm list is identical to the current ones
  static Future<bool> _areAlarmsIdentical(List<AlarmInfo> newAlarms) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final currentStateJson = prefs.getString('current_alarm_state');
      
      if (currentStateJson == null) return false;
      
      final currentState = jsonDecode(currentStateJson) as List<dynamic>;
      
      if (currentState.length != newAlarms.length) return false;
      
      for (int i = 0; i < newAlarms.length; i++) {
        final newAlarm = newAlarms[i];
        final currentAlarm = currentState[i] as Map<String, dynamic>;
        
        if (newAlarm.id != currentAlarm['id'] ||
            newAlarm.name != currentAlarm['name'] ||
            newAlarm.alarm.millisecondsSinceEpoch != currentAlarm['alarm_millis'] ||
            newAlarm.vibratePref != currentAlarm['vibrate'] ||
            newAlarm.player?.id != currentAlarm['player_id'] ||
            newAlarm.player?.name != currentAlarm['player_name'] ||
            newAlarm.player?.table != currentAlarm['player_table']) {
          return false;
        }
      }
      
      return true;
    } catch (e) {
      Log.debug('Error comparing alarms: $e');
      return false;
    }
  }

  /// Alternative alarm setting approach for background contexts
  static Future<void> _setAlarmSafely(DateTime when, String title, String body, int id, bool vibrate) async {
    try {
      // First try the normal approach
      await setAlarm(when, title, body, id, vibrate);
    } catch (e) {
      Log.debug('Normal alarm setting failed, attempting background approach: $e');
      
      // If that fails, try background alarm modification approach
      try {
        // Check if alarm already exists
        final existingAlarm = await Alarm.getAlarm(id);
        
        if (existingAlarm != null) {
          // Modify existing alarm
          Log.debug('Modifying existing alarm $id');
          // Use background alarm service modification if available
          // For now, we'll just log that we would use this approach
          Log.debug('Would use background alarm modification for alarm $id');
        } else {
          // Create new alarm with different approach
          Log.debug('Creating new alarm $id with alternative approach');
          // For now, just rethrow the original error
          rethrow;
        }
      } catch (e2) {
        Log.error('Background alarm approach also failed: $e2');
        rethrow;
      }
    }
  }

  /// Updates the system alarms (background-friendly version)
  static Future<void> _updateSystemAlarms(List<AlarmInfo> alarmInfos, {dynamic ref}) async {
    try {
      final now = DateTime.now().toUtc();
      Log.debug('Current time (UTC): ${now.toIso8601String()}');
      
      // Determine if we're in background context
      final isBackground = ref == null;
      Log.debug('Running in background context: $isBackground');
      
      if (!isBackground) {
        // Only try stopAll() in foreground context
        Log.debug('Attempting to stop all existing alarms (foreground)');
        try {
          await Alarm.stopAll().timeout(const Duration(seconds: 5));
          Log.debug('✅ All alarms stopped successfully');
        } catch (e) {
          Log.error('⚠️  Error stopping alarms: $e');
        }
      } else {
        Log.debug('🚫 SKIPPING stopAll() in background context - will overwrite existing alarms');
      }
      
      // Set new alarms
      Log.debug('📋 Setting ${alarmInfos.length} new alarms');
      int successCount = 0;
      int failureCount = 0;
      
      for (final (index, alarm) in alarmInfos.indexed) {
        final alarmTimeUtc = alarm.alarm.toUtc();
        Log.debug('🔍 Processing alarm $index: ${alarm.name}');
        Log.debug('  ⏰ Alarm time (UTC): ${alarmTimeUtc.toIso8601String()}');
        Log.debug('  📅 Is in future: ${now.isBefore(alarmTimeUtc)}');
        
        if (now.isBefore(alarmTimeUtc)) {
          final title = '${alarm.name} starts in 5 minutes';
          final body = alarm.player != null
              ? '${alarm.player!.name} is at table ${alarm.player!.table}'
              : '';
          
          Log.debug('⚡ Setting alarm ${index + 1}: $title');
          
          try {
            await setAlarm(
              alarmTimeUtc,
              title,
              body,
              index + 1,
              alarm.vibratePref,
            ).timeout(const Duration(seconds: 10));
            successCount++;
            Log.debug('✅ Alarm ${index + 1} set successfully');
          } catch (e) {
            failureCount++;
            Log.error('❌ Failed to set alarm ${index + 1}: $e');
          }
        } else {
          Log.debug('⏭️  Skipping past alarm $index: ${alarm.name}');
        }
      }
      
      Log.debug('🏁 System alarm update completed: $successCount successful, $failureCount failed');
      
      if (successCount > 0) {
        Log.debug('🎉 Background alarm update was successful!');
      } else if (alarmInfos.where((a) => now.isBefore(a.alarm.toUtc())).isNotEmpty) {
        Log.error('💔 No alarms were set despite having future alarms available');
      }
      
    } catch (e) {
      Log.error('💥 Critical error updating system alarms: $e');
    }
  }

  /// Stores the current alarm state for comparison
  static Future<void> _storeCurrentAlarmState(List<AlarmInfo> alarmInfos, SharedPreferences prefs) async {
    try {
      final alarmState = alarmInfos.map((alarm) => {
        'id': alarm.id,
        'name': alarm.name,
        'alarm_millis': alarm.alarm.millisecondsSinceEpoch,
        'vibrate': alarm.vibratePref,
        'player_id': alarm.player?.id,
        'player_name': alarm.player?.name,
        'player_table': alarm.player?.table,
      }).toList();
      
      await prefs.setString('current_alarm_state', jsonEncode(alarmState));
    } catch (e) {
      Log.debug('Error storing alarm state: $e');
    }
  }

  /// Handles schedule update FCM messages in background
  static Future<void> handleScheduleUpdateMessage(RemoteMessage message) async {
    try {
      Log.debug('🚨 AlarmService.handleScheduleUpdateMessage START');
      Log.debug('Timestamp: ${DateTime.now().toIso8601String()}');
      
      final data = message.data;
      final tournamentId = data['tournament_id'];
      final notificationType = data['notification_type'];
      
      Log.debug('Message data validation:');
      Log.debug('  - tournament_id: $tournamentId');
      Log.debug('  - notification_type: $notificationType');
      
      if (tournamentId == null) {
        Log.error('❌ No tournament_id in message data');
        return;
      }
      
      if (notificationType != 'schedule' && notificationType != 'seating') {
        Log.debug('❌ Not a schedule/seating update message (type: $notificationType)');
        return;
      }
      
      Log.debug('✅ Valid schedule/seating update message confirmed');
      
      // Check current app state
      final prefs = await SharedPreferences.getInstance();
      final currentTournamentId = prefs.getString('tournamentId');
      final alarmsEnabled = prefs.getBool('alarm') ?? true;
      
      Log.debug('Current app state check:');
      Log.debug('  - Current tournament: "$currentTournamentId"');
      Log.debug('  - Message tournament: "$tournamentId"');
      Log.debug('  - Alarms enabled: $alarmsEnabled');
      
      if (!alarmsEnabled) {
        Log.debug('❌ Alarms disabled - clearing all alarms and exiting');
        await Alarm.stopAll();
        return;
      }
      
      if (currentTournamentId != tournamentId) {
        Log.debug('❌ Tournament mismatch - message for different tournament');
        return;
      }
      
      Log.debug('✅ Proceeding with alarm update for tournament: $tournamentId');
      
      // Update alarms with the new schedule
      await updateAlarms(
        tournamentId: tournamentId,
        forceUpdate: true,
      );
      
      Log.debug('✅ AlarmService.handleScheduleUpdateMessage COMPLETED');
    } catch (e, stack) {
      Log.error('💥 CRITICAL ERROR in handleScheduleUpdateMessage: $e');
      Log.debug('Full stack trace: $stack');
    }
  }
}

// Provider for the alarm service
final alarmServiceProvider = Provider((ref) => AlarmService._()); 
