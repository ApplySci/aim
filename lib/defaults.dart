import 'utils.dart';

List<Player> PLAYERS = [
  // NB this must be unique, and we must have checked this beforehand
  Player(
    4,
    'Al',
  ),
  Player(
    8,
    'Beauregard',
  ),
  Player(3, 'Frank'),
  Player(
    7,
    'Gogo',
  ),
  Player(
    6,
    'Hubble',
  ),
  Player(
    5,
    'Indigo',
  ),
  Player(1, 'Zag'),
  Player(2, 'Zig'),
];

// Round, Table, ESWN - player id
const SeatingPlan SEATING = {
  'R1': {
    'start': 'Saturday 09.00',
    'tables': {
      'alef': [1, 2, 3, 4],
      'bet': [5, 6, 7, 8],
    },
  },
  'R2': {
    'start': 'Saturday 11.00',
    'tables': {
      'alef': [2, 4, 6, 8],
      'bet': [1, 3, 5, 7],
    },
  },
  'R3': {
    'start': 'Saturday 14.00',
    'tables': {
      'alef': [3, 4, 1, 6],
      'bet': [2, 7, 8, 5],
    },
  },
};

const Map<String, dynamic> DEFAULT_PREFERENCES = {
  'backgroundColour': DEFAULT_COLOUR_KEY, // Colors.black,
  'japaneseWinds': false,
  'japaneseNumbers': false,
  'serverUrl': 'https://tournaments.mahjong.ie/',
  'playerId': -1, // id of player being focused on
  'tournament': 'cork2024',
};

const List<Map<String, dynamic>> NEW_SCORES = [
  {
    'id': 1,
    'name': 'Player 1',
    'total': 50,
    'roundScores': [0, -24, 49, 91, -11, -30]
  },
  {
    'id': 2,
    'name': 'Player 2 has a very long name and will it overflow or what',
    'total': 200,
    'roundScores': [0, 15, 23, 35, 53, 112]
  },
  {
    'id': 3,
    'name': 'Player 3',
    'total': -105,
    'roundScores': [0, 0, -40, 5, -36, -69]
  },
  {
    'id': 4,
    'name': 'Player 4',
    'total': -145,
    'roundScores': [0, 10, 12, -126, -6, -13]
  },
  {
    'id': 5,
    'name': 'Player 5',
    'total': 50,
    'roundScores': [0, -24, 49, 91, -11, -30]
  },
  {
    'id': 6,
    'name': 'Player 6 has a very long name and will it overflow or what',
    'total': 200,
    'roundScores': [0, 15, 23, 35, 53, 112]
  },
  {
    'id': 7,
    'name': 'Player 7',
    'total': -105,
    'roundScores': [0, 0, -40, 5, -36, -69]
  },
  {
    'id': 8,
    'name': 'Player 8',
    'total': -145,
    'roundScores': [0, 10, 12, -126, -6, -13]
  },
  {
    'id': 9,
    'name': 'Player 9',
    'total': 50,
    'roundScores': [0, -24, 49, 91, -11, -30]
  },
  {
    'id': 10,
    'name': 'Player a has a very long name and will it overflow or what',
    'total': 200,
    'roundScores': [0, 15, 23, 35, 53, 112]
  },
  {
    'id': 11,
    'name': 'Player b',
    'total': -105,
    'roundScores': [0, 0, -40, 5, -36, -69]
  },
  {
    'id': 12,
    'name': 'Player c',
    'total': -145,
    'roundScores': [0, 10, 12, -126, -6, -13]
  },
  {
    'id': 13,
    'name': 'Player d',
    'total': 50,
    'roundScores': [0, -24, 49, 91, -11, -30]
  },
  {
    'id': 14,
    'name': 'Player e has a very long name and will it overflow or what',
    'total': 200,
    'roundScores': [0, 15, 23, 35, 53, 112]
  },
  {
    'id': 15,
    'name': 'Player f',
    'total': -105,
    'roundScores': [0, 0, -40, 5, -36, -69]
  },
  {
    'id': 16,
    'name': 'Player g',
    'total': -145,
    'roundScores': [0, 10, 12, -126, -6, -13]
  },
  {
    'id': 17,
    'name': 'Player h',
    'total': 50,
    'roundScores': [0, -24, 49, 91, -11, -30]
  },
  {
    'id': 18,
    'name': 'Player i has a very long name and will it overflow or what',
    'total': 200,
    'roundScores': [0, 15, 23, 35, 53, 112]
  },
  {
    'id': 19,
    'name': 'Player j',
    'total': -105,
    'roundScores': [0, 0, -40, 5, -36, -69]
  },
  {
    'id': 20,
    'name': 'Player k',
    'total': -145,
    'roundScores': [0, 10, 12, -126, -6, -13]
  },
];
