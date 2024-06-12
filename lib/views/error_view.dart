import 'package:flutter/material.dart';

class ErrorView extends StatelessWidget {
  final Object? error;
  final StackTrace stackTrace;

  const ErrorView({
    required this.error,
    required this.stackTrace,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    debugPrintStack(stackTrace: stackTrace, label: '$error');
    return SingleChildScrollView(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('$error'),
          ExpansionTile(
            title: const Text('tap for details'),
            children: [
              Text('$stackTrace'),
            ],
          ),
        ],
      ),
    );
  }
}

class ErrorScaffold extends StatelessWidget {
  const ErrorScaffold({
    required this.title,
    required this.error,
    required this.stackTrace,
    super.key,
  });

  final Widget title;
  final Object? error;
  final StackTrace stackTrace;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: title),
      body: ErrorView(
        error: error,
        stackTrace: stackTrace,
      ),
    );
  }
}
