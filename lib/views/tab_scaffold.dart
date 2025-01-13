import 'package:flutter/material.dart';

class TabScaffold extends StatelessWidget {
  const TabScaffold({
    required this.title,
    required this.tabs,
    required this.children,
    this.actions,
    super.key,
  }) : assert(tabs.length == children.length);

  final Widget title;
  final List<Tab> tabs;
  final List<Widget> children;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: tabs.length,
      child: Scaffold(
        appBar: AppBar(
          title: title,
          actions: actions,
          bottom: TabBar(tabs: tabs),
        ),
        body: TabBarView(children: children),
      ),
    );
  }
} 