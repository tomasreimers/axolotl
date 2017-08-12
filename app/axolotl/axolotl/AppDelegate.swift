//
//  AppDelegate.swift
//  accelerometer
//
//  Created by Gregory Foster on 10/26/16.
//  Copyright © 2016 Gregory Foster. All rights reserved.
//

import UIKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

  var window: UIWindow?
  
  func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
    // Override point for customization after application launch.
    
    let testViewController = ViewController()
    
    self.window = UIWindow(frame: UIScreen.main.bounds)
    
    self.window!.rootViewController = testViewController;
    
    self.window!.backgroundColor = UIColor.white
    self.window!.makeKeyAndVisible()
    
    return true
  }
}

