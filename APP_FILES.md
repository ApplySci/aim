# Flutter App File Structure

This document outlines the structure and purpose of the Dart files in the /lib directory of the World Riichi Tournament app.

## ./lib/
- [`main.dart`](/lib/main.dart) - Application entry point. Sets up Firebase initialization, permissions, alarms, and the root widget with Riverpod provider scope.
- [`models.dart`](/lib/models.dart) - Data models for the application
- [`providers.dart`](/lib/providers.dart) - Riverpod providers for state management
- [`tournament_list_page.dart`](/lib/tournament_list_page.dart) - Main tournament listing page
- [`utils.dart`](/lib/utils.dart) - Utility functions, enums and constants used across the app. Contains logging functionality, date formatting, and route definitions.
- [`venue.dart`](/lib/venue.dart) - Use the phone's native map app to show the location of the tournament venue

## /lib/views/
- [`alarm_page.dart`](/lib/views/alarm_page.dart) - Alarm functionality for tournament notifications
- [`data_table_2d.dart`](/lib/views/data_table_2d.dart) - Enhanced data table widget with fixed columns/rows support
- [`datatable2_fixed_line.dart`](/lib/views/datatable2_fixed_line.dart) - Data table variant with fixed line functionality
- [`error_view.dart`](/lib/views/error_view.dart) - Error display component
- [`loading_view.dart`](/lib/views/loading_view.dart) - Loading state component
- [`settings_page.dart`](/lib/views/settings_page.dart) - App settings configuration
- [`tab_scaffold.dart`](/lib/views/tab_scaffold.dart) - Common tabbed interface scaffold

### /lib/views/player/
- [`player_page.dart`](/lib/views/player/player_page.dart) - Individual player statistics and information
- [`tabs/stats_tab.dart`](/lib/views/player/tabs/stats_tab.dart) - Player statistics including rankings and score charts

### /lib/views/round/
- [`round_page.dart`](/lib/views/round/round_page.dart) - Shows individual round information with games and scores tabs
- [`tabs/games_tab.dart`](/lib/views/round/tabs/games_tab.dart) - Displays games for the round
- [`tabs/scores_tab.dart`](/lib/views/round/tabs/scores_tab.dart) - Shows scores for the round

### /lib/views/tournament/
- [`tournament_page.dart`](/lib/views/tournament/tournament_page.dart) - Individual tournament view
- [`tabs/info_tab.dart`](/lib/views/tournament/tabs/info_tab.dart) - Tournament information tab showing details, notes, and schedule

