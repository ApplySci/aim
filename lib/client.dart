/*
  communications with server goes here

 */
import 'package:dio/dio.dart';

import 'store.dart';
import 'utils.dart';

class IO {
  static final Dio _io = Dio(
    BaseOptions(
      baseUrl: 'https://tournaments.mahjong.ie/json/',
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

  static Future<void> getPlayers(callback) {
    return download('players').then((map) {
      if (map != null) {
        List<Player> players = [];
        map.forEach((k,v) {
          players.add(Player(k is int ? k : int.parse(k), v));
        });
        callback(players);
      }
    });
  }

  static Future<dynamic> download(String url) async {
    Response<dynamic> response;
    try {
      response = await IO._io.get('$url.json');
      Log.info(response.toString());
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
