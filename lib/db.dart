import 'package:firebase_storage/firebase_storage.dart';
final _storage = FirebaseStorage.instance;
final _headRef = _storage.ref();

// Create a Reference to the file
Reference ref = _storage.ref()
    .child('flutter-tests')
    .child('/some-image.jpg');


Future<dynamic> _downloadBytes(Reference ref) async {
  final bytes = await ref.getData();
/*
'Downloaded ${ref.name} \n from bucket: ${ref.bucket}\n '
'at path: ${ref.fullPath} \n'
'Wrote "${ref.fullPath}" to tmp-${ref.name}',
*/
  return bytes;
}
