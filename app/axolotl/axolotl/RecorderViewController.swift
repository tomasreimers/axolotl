//
//  ViewController.swift
//  Axolotl
//
//  Created by Gregory Foster on 9/2/17.
//  Copyright © 2017 Greg M Foster. All rights reserved.
//

import UIKit
import CoreMotion

class RecorderViewController: UIViewController {

    let manager = CMMotionManager()
    let motionStream = MotionStream(bufferLength: 180)
    var touchRecognizer: UILongPressGestureRecognizer?
    var backgroundTask: UIBackgroundTaskIdentifier = UIBackgroundTaskInvalid
    var touchLocation = CGPoint(x: -2, y: -2)

    required init() {
        super.init(nibName: nil, bundle: nil)
        self.title = "Record"
        touchRecognizer = UILongPressGestureRecognizer(target: self, action: #selector(tapped(_:)))
        touchRecognizer?.minimumPressDuration = 0
    }

    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addGestureRecognizer(touchRecognizer!)
//        registerBackgroundTask()
    }

    override func viewDidAppear(_ animated: Bool) {
        startMotionUpdates()
    }

    override func viewDidDisappear(_ animated: Bool) {
        manager.stopGyroUpdates()
        manager.stopGyroUpdates()
    }

    @objc func tapped(_ gestureRecognizer: UILongPressGestureRecognizer) {
        if gestureRecognizer.state == .began {
            let nonnormal = gestureRecognizer.location(in: self.view)
            touchLocation = CGPoint(x: (nonnormal.x / UIScreen.main.bounds.width) * 2 - 1,
                                    y: (nonnormal.y / UIScreen.main.bounds.height) * 2 - 1)
        }
        if gestureRecognizer.state == .ended {
            touchLocation = CGPoint(x:-2, y:-2)
        }
    }

//    func registerBackgroundTask() {
//        backgroundTask = UIApplication.shared.beginBackgroundTask {
//            print("Starting background task")
//        }
//        assert(backgroundTask != UIBackgroundTaskInvalid)
//        print("Background task registered")
//    }

    func startMotionUpdates() {
        // Capture gyro data
        manager.startGyroUpdates(to: OperationQueue.main, withHandler: {gyroData, _ in
            if let data = gyroData {
                self.motionStream.addGyro(time: data.timestamp,
                                          xLoc: CGFloat(data.rotationRate.x),
                                          yLoc: CGFloat(data.rotationRate.y),
                                          zLoc: CGFloat(data.rotationRate.z),
                                          point: self.touchLocation)

            }
        })
        // Capture accel data
        manager.startAccelerometerUpdates(to: OperationQueue.main, withHandler: {accelData, _ in
            if let data = accelData {
                self.motionStream.addAccel(time: data.timestamp,
                                           xLoc: CGFloat(data.acceleration.x),
                                           yLoc: CGFloat(data.acceleration.y),
                                           zLoc: CGFloat(data.acceleration.z),
                                           point: self.touchLocation)
            }
        })
    }
}
