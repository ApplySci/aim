/*

 Utility functions, enums and constants used across the app

 This should NEVER import things from elsewhere in the app.
 This is to avoid circular dependencies.

 */
import 'dart:async';
import 'dart:convert';

import 'package:alarm/alarm.dart';
import 'package:alarm/model/volume_settings.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum LOG {
  debug,
  info,
  score,
  unusual,
  warn,
  error,
}

enum WhenTournament {
  all,
  live,
  upcoming,
  test,
  past,
}

enum TournamentRules {
  wrLeague,
  wrRules,
  ema,
  other;

  factory TournamentRules.fromString(String value) {
    // First try to match based on the stored format
    return switch (value.toUpperCase()) {
      'WRL' => TournamentRules.wrLeague,
      'WRO' => TournamentRules.wrRules,
      'EMA' => TournamentRules.ema,
      // Then try to match based on enum names
      String name when TournamentRules.values.any(
        (rule) => rule.name.toLowerCase() == name.toLowerCase()
      ) => TournamentRules.values.firstWhere(
        (rule) => rule.name.toLowerCase() == name.toLowerCase()
      ),
      _ => TournamentRules.other,
    };
  }

  String get displayName => switch (this) {
    TournamentRules.wrLeague => 'WRL',
    TournamentRules.wrRules => 'WR other',
    TournamentRules.ema => 'EMA',
    TournamentRules.other => 'Other',
  };
}

// Notification-related constants
const notificationTournamentKey = 'notification_tournament_id';
const notificationTabKey = 'notification_tab';

final GlobalKey<NavigatorState> globalNavigatorKey =
    GlobalKey<NavigatorState>();

String dateRange(Timestamp? startDT, Timestamp? endDT) {
  if (startDT == null || endDT == null) return '';
  final sd = startDT.toDate();
  final ed = endDT.toDate();
  String start = 'ERROR: unassigned dateRange!';
  if (sd.year == ed.year) {
    if (sd.month == ed.month && sd.day == ed.day) {
      start = DateFormat('HH:mm').format(sd);
    } else {
      start = DateFormat('HH:mm d MMM').format(sd);
    }
  } else {
    start = DateFormat('HH:mm d MMM y').format(sd);
  }
  final end = DateFormat('HH:mm d MMM y').format(ed);
  return '$start - $end';
}

class ROUTES {
  static const String home = '/home';
  static const String privacyPolicy = '/privacyPolicy';
  static const String tournaments = '/tournaments';
  static const String tournament = '/tournament';
  static const String player = '/player';
  static const String round = '/round';
}

class Log {
  static List<List<dynamic>> logs = [];
  static bool _initialized = false;
  static late SharedPreferences _prefs;
  static const String _currentRunKey = 'debug_logs_current';
  static const String _previousRunKey = 'debug_logs_previous';
  static const String _lastCleanupKey = 'debug_logs_last_cleanup';

  static Future<void> init() async {
    if (_initialized) return;
    _prefs = await SharedPreferences.getInstance();
    
    // On startup, move current run logs to previous run
    final currentRunLogs = _prefs.getStringList(_currentRunKey) ?? [];
    if (currentRunLogs.isNotEmpty) {
      await _prefs.setStringList(_previousRunKey, currentRunLogs);
      await _prefs.setStringList(_currentRunKey, []);
    }
    
    // Check if we need to clean up old logs (once per day)
    await _cleanupOldLogsIfNeeded();
    
    _initialized = true;
  }

  /// Removes log entries older than 24 hours if it hasn't been checked in the last day
  static Future<void> _cleanupOldLogsIfNeeded() async {
    final now = DateTime.now();
    final lastCleanupString = _prefs.getString(_lastCleanupKey);
    
    // If we've cleaned up in the last 24 hours, don't do it again
    if (lastCleanupString != null) {
      final lastCleanup = DateTime.parse(lastCleanupString);
      if (now.difference(lastCleanup).inHours < 24) {
        return;
      }
    }
    
    // Update the last cleanup time
    await _prefs.setString(_lastCleanupKey, now.toIso8601String());
    
    // Clean up current run logs
    final currentRunLogs = _prefs.getStringList(_currentRunKey) ?? [];
    if (currentRunLogs.isNotEmpty) {
      final cutoffTime = now.subtract(const Duration(hours: 24));
      final filteredLogs = _filterLogsNewerThan(currentRunLogs, cutoffTime);
      
      // Only update if we actually removed something
      if (filteredLogs.length < currentRunLogs.length) {
        await _prefs.setStringList(_currentRunKey, filteredLogs);
      }
    }
    
    // Clean up previous run logs
    final previousRunLogs = _prefs.getStringList(_previousRunKey) ?? [];
    if (previousRunLogs.isNotEmpty) {
      final cutoffTime = now.subtract(const Duration(hours: 24));
      final filteredLogs = _filterLogsNewerThan(previousRunLogs, cutoffTime);
      
      // Only update if we actually removed something
      if (filteredLogs.length < previousRunLogs.length) {
        await _prefs.setStringList(_previousRunKey, filteredLogs);
      }
    }
  }
  
  /// Filters logs to only keep those newer than the cutoff time
  static List<String> _filterLogsNewerThan(List<String> logs, DateTime cutoffTime) {
    return logs.where((logString) {
      try {
        final logEntry = jsonDecode(logString) as List<dynamic>;
        final timestamp = DateTime.parse(logEntry[0] as String);
        return timestamp.isAfter(cutoffTime);
      } catch (e) {
        // If there's an error parsing the log, keep it to be safe
        return true;
      }
    }).toList();
  }

  static void debug(String text) {
    _saveLog(LOG.debug, text);
  }

  static void info(String text) {
    _saveLog(LOG.info, text);
  }

  static void unusual(String text) {
    _saveLog(LOG.unusual, text);
  }

  static void warn(String text) {
    _saveLog(LOG.warn, text);
  }

  static void error(String text) {
    _saveLog(LOG.error, text);
  }

  static void _saveLog(LOG type, String text) {
    final typeString = type.name;
    final timestamp = DateTime.now().toIso8601String();
    final logEntry = [timestamp, typeString, text];
    logs.add(logEntry);

    // Output to debug console in debug mode
    debugPrint('[${typeString.toUpperCase()}] $text');
    
    // Store in SharedPreferences
    if (_initialized) {
      final currentLogs = _prefs.getStringList(_currentRunKey) ?? [];
      currentLogs.add(jsonEncode(logEntry));
      // Keep only the most recent logs in memory (limit to 200)
      if (currentLogs.length > 200) {
        currentLogs.removeAt(0);
      }
      _prefs.setStringList(_currentRunKey, currentLogs);
    }
  }

  static List<List<String>> getAllLogs() {
    if (!_initialized) return [];
    
    final currentRunLogs = _prefs.getStringList(_currentRunKey) ?? [];
    final previousRunLogs = _prefs.getStringList(_previousRunKey) ?? [];
    
    final List<List<String>> allLogs = [];
    
    if (previousRunLogs.isNotEmpty) {
      allLogs.add(['--- Previous Run ---']);
      allLogs.addAll(previousRunLogs.map((log) => 
        _formatLogEntry(jsonDecode(log) as List<dynamic>)).toList());
    }
    
    if (currentRunLogs.isNotEmpty) {
      allLogs.add(['--- Current Run ---']);
      allLogs.addAll(currentRunLogs.map((log) => 
        _formatLogEntry(jsonDecode(log) as List<dynamic>)).toList());
    }
    
    return allLogs;
  }
  
  static List<String> _formatLogEntry(List<dynamic> logEntry) {
    final timestamp = DateTime.parse(logEntry[0] as String).toLocal();
    final timeString = '${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}:${timestamp.second.toString().padLeft(2, '0')}';
    final type = logEntry[1] as String;
    final message = logEntry[2] as String;
    return ['$timeString [${type.toUpperCase()}] $message'];
  }

  static List<String> getLogs() {
    final allLogs = getAllLogs();
    return allLogs.map((entry) => entry.join(' ')).toList();
  }

  static Future<void> clearAllLogs() async {
    if (!_initialized) return;
    await _prefs.setStringList(_currentRunKey, []);
    await _prefs.setStringList(_previousRunKey, []);
    logs.clear();
  }
  
  /// Public method to manually trigger cleaning up of old logs
  static Future<void> cleanupOldLogs() async {
    if (!_initialized) return;
    
    // Force cleanup by resetting the last cleanup time
    await _prefs.remove(_lastCleanupKey);
    await _cleanupOldLogsIfNeeded();
  }
  
  /// Called when app is resumed from background
  /// Checks if logs need to be cleaned up
  static Future<void> onAppResume() async {
    if (!_initialized) return;
    await _cleanupOldLogsIfNeeded();
  }
}

typedef RunOrQueueValue = ({
  Future<void> future,
  FutureOr<void> Function() current,
  FutureOr<void> Function()? next,
});

class RunOrQueue {
  RunOrQueue._();

  RunOrQueueValue? _queue;

  Future<void> call(FutureOr<void> Function() block) async {
    if (_queue case RunOrQueueValue queue) {
      _queue = (
        future: queue.future,
        current: queue.current,
        next: block,
      );
      return await queue.future;
    }

    final completer = Completer<void>();
    _queue = (
      future: completer.future,
      current: block,
      next: null,
    );
    while (_queue != null) {
      try {
        await _queue!.current();
      } finally {
        _queue = switch (_queue) {
          (
            future: Future<void> future,
            current: FutureOr<void> Function() _,
            next: FutureOr<void> Function() current,
          ) =>
            (
              future: future,
              current: current,
              next: null,
            ),
          _ => null,
        };
      }
    }
    completer.complete();
  }
}

final alarmRunner = RunOrQueue._();

// Function to store alarm ID
Future<void> setAlarm(
  DateTime when,
  String title,
  String body,
  int id,
  bool vibrate,
) async {
  final alarmSettings = AlarmSettings(
      id: id,
      dateTime: when,
      androidFullScreenIntent: false,
      assetAudioPath: 'assets/audio/notif.mp3',
      loopAudio: false,
      vibrate: vibrate,
      volumeSettings: VolumeSettings.fixed(),
      notificationSettings: NotificationSettings(
        title: title,
        body: body,
        stopButton: "Dismiss",
        icon: "ic_launcher",
      ));
  await Alarm.set(alarmSettings: alarmSettings);
}

extension SeparatedBy<T> on Iterable<T> {
  Iterable<T> separatedBy(T seperator) sync* {
    if (isEmpty) return;

    final iterator = this.iterator;
    iterator.moveNext();
    yield iterator.current;
    while (iterator.moveNext()) {
      yield seperator;
      yield iterator.current;
    }
  }
}
