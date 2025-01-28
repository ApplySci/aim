import 'package:flutter/material.dart';
import '/utils.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  const CustomAppBar({
    required this.title,
    this.showHomeButton = true,
    this.actions,
    this.leading,
    super.key,
  });

  final Widget title;
  final bool showHomeButton;
  final List<Widget>? actions;
  final Widget? leading;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      automaticallyImplyLeading: false,
      title: title,
      leading: leading ?? (showHomeButton
          ? IconButton(
              icon: const Icon(Icons.home),
              onPressed: () {
                Navigator.of(context).pushNamedAndRemoveUntil(
                  ROUTES.home,
                  (route) => false,
                );
              },
            )
          : null),
      actions: actions,
    );
  }
}
