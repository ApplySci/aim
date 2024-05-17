Looks like there's an irrecoverable crash in fcm_client L54
if there's no network available

FLTFirebaseMessaging: An error occurred while calling method Messaging#getToken, errorOrNil => {
    NSErrorFailingURLKey = "https://device-provisioning.googleapis.com/checkin";
    NSErrorFailingURLStringKey = "https://device-provisioning.googleapis.com/checkin";
    NSLocalizedDescription = "The request timed out.";
    "_NSURLErrorFailingURLSessionTaskErrorKey" = "LocalDataTask <EB6BD589-9803-4298-BCA9-54F82D237C72>.<1>";
    "_NSURLErrorRelatedURLSessionTaskErrorKey" =     (
        "LocalDataTask <EB6BD589-9803-4298-BCA9-54F82D237C72>.<1>"
    );
    "_kCFStreamErrorCodeKey" = "-2103";
    "_kCFStreamErrorDomainKey" = 4;
}
[ERROR:flutter/runtime/dart_vm_initializer.cc(41)] Unhandled Exception: [firebase_messaging/unknown] The request timed out.
#0      StandardMethodCodec.decodeEnvelope (package:flutter/src/services/message_codecs.dart:651:7)
#1      MethodChannel._invokeMethod (package:flutter/src/services/platform_channel.dart:334:18)
<asynchronous suspension>
#2      MethodChannel.invokeMapMethod (package:flutter/src/services/platform_channel.dart:534:43)
<asynchronous suspension>
#3      MethodChannelFirebaseMessaging.getToken (package:firebase_messaging_platform_interface/src/method_channel/method_channel_messaging.dart:248:11)
<asynchronous suspension>
#4      getFCMToken (package:aim_tournaments/fcm_client.dart:54:27)
<asynchronous suspension>
#5      setupFCM (package:aim_tournaments/fcm_client.dart:13:3)
<asynchronous suspension>
#6      main (package:aim_tournaments/main.dart:29:3)
<asynchronous suspension>

