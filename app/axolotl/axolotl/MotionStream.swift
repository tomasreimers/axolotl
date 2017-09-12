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

class MotionStream: NSObject {
    let bufferLength: Int
    var gyroMoments: [SimpleMoment] = []
    var accelMoments: [SimpleMoment] = []

    init(bufferLength: Int) {
        self.bufferLength = bufferLength
        super.init()
    }

    func addGyro(time: TimeInterval, xLoc: CGFloat, yLoc: CGFloat, zLoc: CGFloat, point: CGPoint) {
        gyroMoments.insert(SimpleMoment(time:time, xLoc:xLoc, yLoc:yLoc, zLoc:zLoc, point:point), at:0)
    }

    func addAccel(time: TimeInterval, xLoc: CGFloat, yLoc: CGFloat, zLoc: CGFloat, point: CGPoint) {
        accelMoments.insert(SimpleMoment(time:time, xLoc:xLoc, yLoc:yLoc, zLoc:zLoc, point:point), at:0)
    }

    func getGyroData() -> [SimpleMoment] {
        return gyroMoments
    }

    func getAccelData() -> [SimpleMoment] {
        return accelMoments
    }

    func getGyroAndAccel() -> ([SimpleMoment], [SimpleMoment]) {
        return (gyroMoments, accelMoments)
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
