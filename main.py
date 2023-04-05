import airsim
import os
import cv2
import sys
import time

# ----------------- SETTING -----------------#
import numpy as np

cameraTypeMap = {
    "depth": airsim.ImageType.DepthVis,
    "segmentation": airsim.ImageType.Segmentation,
    "seg": airsim.ImageType.Segmentation,
    "scene": airsim.ImageType.Scene,
    "disparity": airsim.ImageType.DisparityNormalized,
    "normals": airsim.ImageType.SurfaceNormals
}

cameraNameMap = ["front_center", "front_right", "front_left", "fpv", "bottom_center", "back_center"]

# set camera parameters
cameraType = "scene"
if cameraType not in cameraTypeMap:
    sys.exit(1)
else:
    print(cameraTypeMap[cameraType])

cameraName = "front_center"
if cameraName not in cameraNameMap:
    sys.exit(1)
else:
    print(cameraName)

# Set Parameters for timestamps
fontFace = cv2.FONT_HERSHEY_PLAIN
fontScale = 1
thickness = 1
textSize, baseline = cv2.getTextSize("FPS", fontFace, fontScale, thickness)
textOrg = (10, 10 + textSize[1])

# set/create image folder directory
directory = "generated-data"
if not os.path.exists(directory):
    os.makedirs(directory)

# ----------------- FLYING -----------------#

# connect to the AirSim simulator using Tornado
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

# take off
startTime = time.time()
client.takeoffAsync().join()

# Capture Images
for i in range(10):
    # move forward
    client.moveByVelocityAsync(5, 0, 0, 0.1).join()
    endTime = time.time()
    diff = endTime - startTime
    # capture image
    raw = client.simGetImage(cameraName, cameraTypeMap[cameraType])
    if raw is None:
        print("Camera is not returning image, please check airsim for error messages")
        sys.exit(0)
    else:
        png = cv2.imdecode(airsim.string_to_uint8_array(raw), cv2.IMREAD_UNCHANGED)
        img_name = 'Frame:'+str(i) + ' ' 'Time:' + str("{:.2f}".format(diff))
        cv2.putText(png, img_name, textOrg, fontFace, fontScale, (0, 255, 255), thickness)
        file_name = 'Frame ' + str(i) + '.png'
        cv2.imwrite(os.path.join(directory, file_name), png)

# Land Drone
client.landAsync().join()

# Reset Position of Drone
client.reset()

# Disconnect from AirSim
client.enableApiControl(False)
