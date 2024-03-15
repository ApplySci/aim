import 'package:dio/dio.dart';

import 'store.dart';
import 'utils.dart';

class IO {
  IO._singleton();
  static Dio dio = Dio(
    BaseOptions(
      baseUrl: 'https://tournaments.mahjong.ie/',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      validateStatus: (status) {
        return status! < 500;
      },
    ),
  );
}
// TODO communications with server goes here
