# Flutter App File Structure

This document outlines the structure and purpose of the Dart files in the /lib directory of the World Riichi Tournament app.

## ./lib/
- `main.dart` - Application entry point. Sets up Firebase initialization, permissions, alarms, and the root widget with Riverpod provider scope.
- `models.dart` - Data models for the application
- `providers.dart` - Riverpod providers for state management
- `utils.dart` - Utility functions, enums and constants used across the app. Contains logging functionality, date formatting, and route definitions.
- `venue.dart` - Use the phone's native map app to show the location of the tournament venue

## /lib/views/
- `views/alarm_page.dart` - Alarm functionality for tournament notifications
- `views/data_table_2d.dart` - Enhanced data table widget with fixed columns/rows support
- `views/datatable2_fixed_line.dart` - Data table variant with fixed line functionality
- `views/error_view.dart` - Error display component
- `views/loading_view.dart` - Loading state component
- `views/settings_page.dart` - App settings configuration
- `views/tab_scaffold.dart` - Common tabbed interface scaffold

### /lib/views/player/
- `views/player/player_page.dart` - Individual player statistics and information
- `views/player/tabs/stats_tab.dart` - Player statistics including rankings and score charts

### /lib/views/round/
- `views/round/round_page.dart` - Shows individual round information with games and scores tabs
- `views/round/tabs/games_tab.dart` - Displays games for the round
- `views/round/tabs/scores_tab.dart` - Shows scores for the round

### /lib/views/tournament/
- `views/tournament_list_page.dart` - Main tournament listing page
- `views/tournament/tournament_page.dart` - Individual tournament view
- `views/tournament/tabs/info_tab.dart` - Tournament information tab showing details, notes, and schedule

