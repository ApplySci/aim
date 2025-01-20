# Flutter App File Structure

This document outlines the structure and purpose of the Dart files in the /lib directory of the World Riichi Tournament app.

# ./lib/ The Flutter application
- [`main.dart`](/lib/main.dart) - Application entry point. Sets up Firebase initialization, permissions, alarms, and the root widget with Riverpod provider scope.
- [`models.dart`](/lib/models.dart) - Data models for the application
- [`providers.dart`](/lib/providers.dart) - Riverpod providers for state management
- [`tournament_list_page.dart`](/lib/tournament_list_page.dart) - Main list of past/present/future tournaments
- [`utils.dart`](/lib/utils.dart) - Utility functions, enums and constants used across the app. Contains logging functionality, date formatting, and route definitions.
- [`venue.dart`](/lib/venue.dart) - Use the phone's native map app to show the location of the tournament venue

## /lib/providers/ Riverpod providers
- [`fcm.dart`](/lib/providers/fcm.dart) - Firebase Cloud Messaging provider and initialization
- [`firestore.dart`](/lib/providers/firestore.dart) - Firestore database access and tournament data providers
- [`location.dart`](/lib/providers/location.dart) - Location and timezone providers
- [`seat_map.dart`](/lib/providers/seat_map.dart) - Tournament seating map providers
- [`shared_preferences.dart`](/lib/providers/shared_preferences.dart) - Local storage preferences providers

## /lib/views/
- [`alarm_page.dart`](/lib/views/alarm_page.dart) - Alarm functionality for tournament notifications
- [`app_bar.dart`](/lib/views/app_bar.dart) - Custom app nav bar component
- [`data_table_2d.dart`](/lib/views/data_table_2d.dart) - Customised version of the data_table_2 package, enchanced with a fixed bottom row, for the ranking table
- [`datatable2_fixed_line.dart`](/lib/views/datatable2_fixed_line.dart) - Data table variant with fixed line functionality
- [`error_view.dart`](/lib/views/error_view.dart) - Error display. The user shouldn't see this if everything goes well: it's here for debugging.
- [`loading_view.dart`](/lib/views/loading_view.dart) - Loading state
- [`my_spark_chart.dart`](/lib/views/my_spark_chart.dart) - Customizable chart component using SfCartesianChart for line and bar visualizations with data labels
- [`rank_text.dart`](/lib/views/rank_text.dart) - Text formatting component for player rankings and positions
- [`schedule_list.dart`](/lib/views/schedule_list.dart) - Tournament schedule list view with filtering
- [`score_text.dart`](/lib/views/score_text.dart) - Score display formatting with polarity colouring
- [`settings_page.dart`](/lib/views/settings_page.dart) - User settings
- [`tab_scaffold.dart`](/lib/views/tab_scaffold.dart) - Generic tabbed interface scaffold with customizable tabs and actions
- [`table_score_table.dart`](/lib/views/table_score_table.dart) - Table component for displaying game scores
- [`viewutils.dart`](/lib/views/viewutils.dart) - Shared utilities for view components including text sizing and formatting

### /lib/views/player/
- [`player_page.dart`](/lib/views/player/player_page.dart) - Information specific to one player
- [`tabs/games_tab.dart`](/lib/views/player/tabs/games_tab.dart) - Player's game history and results
- [`tabs/schedule_tab.dart`](/lib/views/player/tabs/schedule_tab.dart) - Player's seating
- [`tabs/scores_tab.dart`](/lib/views/player/tabs/scores_tab.dart) - Player's hanchan results
- [`tabs/stats_tab.dart`](/lib/views/player/tabs/stats_tab.dart) - Player's statistics including current score, penalties, averages, and trend charts

### /lib/views/round/
- [`round_page.dart`](/lib/views/round/round_page.dart) - Individual round information with games and scores tabs
- [`tabs/games_tab.dart`](/lib/views/round/tabs/games_tab.dart) - Displays games for the round
- [`tabs/scores_tab.dart`](/lib/views/round/tabs/scores_tab.dart) - Shows scores for the round

### /lib/views/tournament/
- [`tabs/tournament_page.dart`](/lib/views/tournament/tournament_page.dart) - Individual tournament view
- [`tabs/round_list_tab.dart`](/lib/views/tournament/tabs/round_list_tab.dart) - seating
- [`tabs/score_tab.dart`](/lib/views/tournament/tabs/score_tab.dart) - ranking
- [`tabs/player_list_tab.dart`](/lib/views/tournament/tabs/player_list_tab.dart) - Searchable list of players
- [`tabs/info_tab.dart`](/lib/views/tournament/tabs/info_tab.dart) - Tournament metadata including logo, website, location, notes, and schedule table with timezone support
