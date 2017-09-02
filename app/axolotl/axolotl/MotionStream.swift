//
//  MotionStream.swift
//  Axolotl
//
//  Created by Gregory Foster on 9/2/17.
//  Copyright © 2017 Greg M Foster. All rights reserved.
//

import UIKit

struct SimpleMoment {
    var time: TimeInterval = 0
    var xLoc: CGFloat = 0
    var yLoc: CGFloat = 0
    var zLoc: CGFloat = 0
    var point: CGPoint = CGPoint(x: -2, y: -2)
}

class MotionStream {
    let bufferLength: TimeInterval = 180
    var gyroMoments: [SimpleMoment] = []
    var accelMoments: [SimpleMoment] = []

    func addGyro(time: TimeInterval, xLoc: CGFloat, yLoc: CGFloat, zLoc: CGFloat, point: CGPoint) {
        gyroMoments.insert(SimpleMoment(time:time, xLoc:xLoc, yLoc:yLoc, zLoc:zLoc, point:point), at:0)
        if let first = gyroMoments.first?.time, let last = gyroMoments.last?.time {
            let timeElapsed = abs(last - first)
            print(timeElapsed)
            if timeElapsed  > bufferLength {
                snapshot(type: "GYRO", moments: gyroMoments)
                snapshot(type: "ACCEL", moments: accelMoments)
                accelMoments = []
                gyroMoments = []
            }
        }
    }

    func addAccel(time: TimeInterval, xLoc: CGFloat, yLoc: CGFloat, zLoc: CGFloat, point: CGPoint) {
        accelMoments.insert(SimpleMoment(time:time, xLoc:xLoc, yLoc:yLoc, zLoc:zLoc, point:point), at:0)
        if let first = accelMoments.first?.time, let last = accelMoments.last?.time {
            if abs(last - first) > bufferLength {
                snapshot(type: "GYRO", moments: gyroMoments)
                snapshot(type: "ACCEL", moments: accelMoments)
                accelMoments = []
                gyroMoments = []
            }
        }
    }

    func getGyroData() -> [SimpleMoment] {
        return gyroMoments
    }

    func getAccelData() -> [SimpleMoment] {
        return accelMoments
    }

    func snapshot(type: String, moments: [SimpleMoment]) {
        let fileName = "\(type)_STREAM_\(NSDate().timeIntervalSince1970).txt"
        var text = "touch_x, touch_y, sensor_type, time_since_1970, x, y, z\n"
        for m in moments {
            text += "\(m.point.x), \(m.point.y), \(type), \(m.time), \(m.xLoc), \(m.yLoc), \(m.zLoc)\n"
        }

        if let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first {
            let path = dir.appendingPathComponent(fileName)
            do {
                try text.write(to: path, atomically: false, encoding: String.Encoding.utf8)
            } catch {/* error handling here */}
            print("Wrote \(moments.count) \(type) moments")
        }
    }
}
