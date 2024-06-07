import 'dart:io' show Platform;
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

Uri googleMapsUrl(String address) =>
    Uri.parse('https://www.google.com/maps/search/?api=1&query=$address');

Uri appleMapsUrl(String address) =>
    Uri.parse('https://maps.apple.com/?q=$address');

Future<bool> tryLaunchUrl(Uri url) => launchUrl(url).onError((_, __) => false);

/*
 This will open the default map app at the address of the venue
 The address can be any google/apple address query. Two examples:
 1) latitude,longitude: "53.5831819,-0.0728641"
 2) text address: "grimsby dock tower, uk"
 */
Future<void> openMap(BuildContext context, String address) async {
  final safeAddress = Uri.encodeQueryComponent(address);
  if (Platform.isIOS || Platform.isMacOS) {
    if (await tryLaunchUrl(appleMapsUrl(safeAddress))) return;
    if (await tryLaunchUrl(googleMapsUrl(safeAddress))) return;
  } else {
    if (await tryLaunchUrl(googleMapsUrl(safeAddress))) return;
    if (await tryLaunchUrl(appleMapsUrl(safeAddress))) return;
  }

  if (!context.mounted) return;
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(content: Text('unable to launch map')),
  );
}
