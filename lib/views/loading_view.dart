import 'package:flutter/material.dart';

class LoadingView extends StatelessWidget {
  const LoadingView({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: CircularProgressIndicator());
  }
}

class LoadingScaffold extends StatelessWidget {
  const LoadingScaffold({
    required this.title,
    super.key,
  });

  final Widget title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: title),
      body: const LoadingView(),
    );
  }
}
