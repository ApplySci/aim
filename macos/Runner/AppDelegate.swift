import Cocoa
import FlutterMacOS
import UserNotifications
import alarm

@main
class AppDelegate: FlutterAppDelegate {
  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
      if #available(iOS 10.0, *) {
          UNUserNotificationCenter.current().delegate = self as UNUserNotificationCenterDelegate
      }
      SwiftAlarmPlugin.registerBackgroundTasks()
      
      GeneratePluginRegistrant.register(with: self)
      return super.application(application, didFinishLaunchingWithOptions:
                                launchOptions)
  }
}
