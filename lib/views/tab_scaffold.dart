import 'package:flutter/material.dart';

class TabScaffold extends StatelessWidget {
  const TabScaffold({
    required this.title,
    required this.tabs,
    required this.children,
    this.actions,
    this.filterBar,
    this.automaticallyImplyLeading = true,
    super.key,
  }) : assert(tabs.length == children.length);

  final Widget title;
  final List<Tab> tabs;
  final List<Widget> children;
  final List<Widget>? actions;
  final Widget? filterBar;
  final bool automaticallyImplyLeading;

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: tabs.length,
      child: Scaffold(
        appBar: AppBar(
          automaticallyImplyLeading: automaticallyImplyLeading,
          title: title,
          actions: actions,
          bottom: TabBar(tabs: tabs),
        ),
        body: Column(
          children: [
            if (filterBar != null) filterBar!,
            Expanded(
              child: TabBarView(children: children),
            ),
          ],
        ),
      ),
    );
  }
} 