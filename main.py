import airsim
import os
import cv2
import sys
import time
from airsim import Vector3r

# ----------------- SETTING -----------------#

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

cameraName = "bottom_center"
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
def captureImages(i):
    # capture image
    raw = client.simGetImage(cameraName, cameraTypeMap[cameraType])
    drone_position = client.simGetVehiclePose().position
    t = Vector3r(drone_position.x_val, drone_position.y_val, drone_position.z_val)
    x_val = "{:.2f}".format(t.x_val)
    y_val = "{:.2f}".format(t.y_val)
    z_val = "{:.2f}".format(t.z_val)
    str_position = 'x:' + x_val + ' ' + 'y: ' + y_val + ' ' + 'z:' + z_val
    # print(str_position)
    if raw is None:
        print("Camera is not returning image, please check airsim for error messages")
        sys.exit(0)
    else:
        png = cv2.imdecode(airsim.string_to_uint8_array(raw), cv2.IMREAD_UNCHANGED)
        img_name = str_position
        cv2.putText(png, img_name, textOrg, fontFace, fontScale, (0, 255, 255), thickness)
        file_name = 'Frame ' + str(i) + '.png'
        cv2.imwrite(os.path.join(directory, file_name), png)


def performCycle(velocity):
    for i in range(10):
        # move forward
        client.moveByVelocityAsync(velocity, 0, 0, 1).join()
        captureImages(i)

    for i in range(10, 17):
        # move left
        client.moveByVelocityAsync(0, velocity, 0, 1).join()
        captureImages(i)

    for i in range(17, 25):
        # move left
        client.moveByVelocityAsync(-velocity, 0, 0, 1).join()
        captureImages(i)

    for i in range(25, 31):
        # move left
        client.moveByVelocityAsync(0, -velocity, 0, 1).join()
        captureImages(i)


# connect to the AirSim simulator using Tornado
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

# take off
client.takeoffAsync().join()
for i in range(3):
    client.moveByVelocityAsync(0, 7, 0, 1).join()
# Fly
velocity = 10
performCycle(velocity)

# Land Drone
client.landAsync().join()

# Reset Position of Drone
client.reset()

# Disconnect from AirSim
client.enableApiControl(False)
