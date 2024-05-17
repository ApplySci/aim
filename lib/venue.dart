import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

/*
 This will open the default map app at the address of the venue
 The address can be any google/apple address query. Two examples:
 1) latitude,longitude: "53.5831819,-0.0728641"
 2) text address: "grimsby dock tower, uk"
 */
void openMap(BuildContext context, String address) async {
  final safeAddress = Uri.encodeQueryComponent(address);
  final Uri googleUrl =
      Uri.parse('https://www.google.com/maps/search/?api=1&query=$safeAddress');
  bool success = false;
  try {
    success = await launchUrl(googleUrl);
  } catch (_) {
    success = false;
  }
  if (!success) {
    try {
      final Uri appleUrl = Uri.parse("https://maps.apple.com/?q=$safeAddress");
      success = await launchUrl(appleUrl);
    } catch (_) {
      success = false;
    }
  }
  if (!success && context.mounted) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("unable to launch map")),
    );
  }
}
