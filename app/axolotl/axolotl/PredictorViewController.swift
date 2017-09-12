//
//  PredictorViewController.swift
//  Axolotl
//
//  Created by Gregory Foster on 9/11/17.
//  Copyright © 2017 Greg M Foster. All rights reserved.
//

import UIKit
import CoreMotion
import CoreML

class PredictorViewController: UIViewController {

    let manager = CMMotionManager()
    let motionStream = MotionStream(bufferLength: 20)
    var backgroundTask: UIBackgroundTaskIdentifier = UIBackgroundTaskInvalid
    var touchLocation = CGPoint(x: -2, y: -2)
    let touchModel = touch_model()
    let locationhModel = location_model()

    required init() {
        super.init(nibName: nil, bundle: nil)
        self.title = "Predict"
    }

    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
    }

    override func viewDidAppear(_ animated: Bool) {
        startMotionUpdates()
    }

    override func viewDidDisappear(_ animated: Bool) {
        manager.stopGyroUpdates()
        manager.stopGyroUpdates()
    }

    func startMotionUpdates() {
        // Capture gyro data
        manager.startGyroUpdates(to: OperationQueue.main, withHandler: {gyroData, _ in
            if let data = gyroData {
                self.motionStream.addGyro(time: data.timestamp,
                                          xLoc: CGFloat(data.rotationRate.x),
                                          yLoc: CGFloat(data.rotationRate.y),
                                          zLoc: CGFloat(data.rotationRate.z),
                                          point: CGPoint.zero)

            }
        })
        // Capture accel data
        manager.startAccelerometerUpdates(to: OperationQueue.main, withHandler: {accelData, _ in
            if let data = accelData {
                self.motionStream.addAccel(time: data.timestamp,
                                           xLoc: CGFloat(data.acceleration.x),
                                           yLoc: CGFloat(data.acceleration.y),
                                           zLoc: CGFloat(data.acceleration.z),
                                           point: CGPoint.zero)
            }
        })
    }

    func predict() {
        let (gyroData, accelData) = motionStream.getGyroAndAccel()
        assert(gyroData.count == accelData.count)

        guard let input = try? MLMultiArray(shape:[120], dataType:.double) else {
            fatalError("Unexpected runtime error. MLMultiArray")
        }
        for index in 0..<gyroData.count {
            input[index * 6 + 0] = NSNumber(value: Float(accelData[index].xLoc))
            input[index * 6 + 1] = NSNumber(value: Float(accelData[index].yLoc))
            input[index * 6 + 2] = NSNumber(value: Float(accelData[index].zLoc))
            input[index * 6 + 3] = NSNumber(value: Float(gyroData[index].xLoc))
            input[index * 6 + 4] = NSNumber(value: Float(gyroData[index].yLoc))
            input[index * 6 + 5] = NSNumber(value: Float(gyroData[index].zLoc))
        }
        guard let predictionOutput = try? touchModel.prediction(input: touch_modelInput(touch_windows: input)) else {
            fatalError("Unexpected runtime error. model.prediction")
        }
        print(predictionOutput.touch_predictions)
    }
}
