/*
  communications with server goes here

 */
import 'package:dio/dio.dart';

import 'store.dart';
import 'utils.dart';

class IO {
  static final Dio _io = Dio(
    BaseOptions(
      baseUrl: 'https://tournaments.mahjong.ie/',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        "Accept": "application/json",
      },
      validateStatus: (status) {
        return status! < 500;
      },
    ),
  );

  static Future<void> getPlayers() {
    return download('json/players').then((players) {
      if (players == null) {
        return;
      }
      store.dispatch({
        'type': STORE.setPlayerList,
        'players': players,
      });
    });
  }

  static Future<void> getScores() {
    return download('json/scores').then((scores) {
      if (scores != null) {
        store.dispatch({
          'type': STORE.setScores,
          'scores': List<Map<String, dynamic>>.from(scores),
        });
      }
    });
  }

  static Future<void> getSeating() {
    return download('json/seating').then((seating) {
      if (seating != null) {
        store.dispatch({
          'type': STORE.setSeating,
          'seating': seating,
        });
      }
    });
  }

  void sendToken(String token) async {
    Response<dynamic> response = await IO._io.post(
      'client/token',
      queryParameters: {'token': token},
    );
  }

  static Future<dynamic> download(String url) async {
    Response<dynamic> response;
    try {
      response = await IO._io.get('$url.json');
      Log.info('downloaded ${response.toString()}');
      return response.data;
    } on DioException catch (e) {
      if (e.response == null) {
        Log.error(e.message!);
        Log.info(e.requestOptions.toString());
      } else {
        // Something happened in setting up or sending the request that triggered an Error
        Log.error(e.response!.headers.toString());
        Log.info(e.response!.data.toString());
        Log.info(e.response!.requestOptions.toString());
      }
    }
    return null;
  }
}
