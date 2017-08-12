//
//  MotionStream.swift
//  accelerometer
//
//  Created by Gregory Foster on 10/30/16.
//  Copyright © 2016 Gregory Foster. All rights reserved.
//

import UIKit

struct SimpleMoment {
  var time:TimeInterval = 0
  var x:CGFloat = 0
  var y:CGFloat = 0
  var z:CGFloat = 0
  var point:CGPoint = CGPoint(x: -2, y: -2)
}

class MotionStream {
  let bufferLength: TimeInterval = 180;
  var gyroMoments: [SimpleMoment] = []
  var accelMoments: [SimpleMoment] = []
  
  func addGyro(time:TimeInterval, x:CGFloat, y:CGFloat, z:CGFloat, point:CGPoint) {
    gyroMoments.insert(SimpleMoment(time:time, x:x, y:y, z:z, point:point), at:0)
    if let first = gyroMoments.first?.time, let last = gyroMoments.last?.time {
      let timeElapsed = abs(last - first)
      print(timeElapsed)
      if (timeElapsed  > bufferLength) {
        snapshot(type: "GYRO", moments: gyroMoments)
        snapshot(type: "ACCEL", moments: accelMoments)
        accelMoments = []
        gyroMoments = []
      }
    }
  }
  
  func addAccel(time:TimeInterval, x:CGFloat, y:CGFloat, z:CGFloat, point:CGPoint) {
    accelMoments.insert(SimpleMoment(time:time, x:x, y:y, z:z, point:point), at:0)
    if let first = accelMoments.first?.time, let last = accelMoments.last?.time {
      if (abs(last - first) > bufferLength) {
        snapshot(type: "GYRO", moments: gyroMoments)
        snapshot(type: "ACCEL", moments: accelMoments)
        accelMoments = []
        gyroMoments = []
      }
    }
  }
  
  func getGyroData() -> [SimpleMoment] {
    return gyroMoments;
  }
  
  func getAccelData() -> [SimpleMoment] {
    return accelMoments;
  }
  
  func snapshot(type:String, moments:[SimpleMoment]) {
    let fileName = "\(type)_STREAM_\(NSDate().timeIntervalSince1970).txt"
    var text = "touch_x, touch_y, sensor_type, time_since_1970, x, y, z\n"
    for moment in moments {
      text += "\(moment.point.x), \(moment.point.y), \(type), \(moment.time), \(moment.x), \(moment.y), \(moment.z)\n"
    }
    
    if let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first {
      let path = dir.appendingPathComponent(fileName)
      do {
        try text.write(to: path, atomically: false, encoding: String.Encoding.utf8)
      }
      catch {/* error handling here */}
      print("Wrote \(moments.count) \(type) moments")
    }
  }
}
