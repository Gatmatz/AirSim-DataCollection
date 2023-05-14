import datetime

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


def setCameraType(cameraType):
    if cameraType not in cameraTypeMap:
        sys.exit(1)
    else:
        return cameraType


def setCameraName(cameraName):
    if cameraName not in cameraNameMap:
        sys.exit(1)
    else:
        return cameraName


# set/create image folder directory
def createDirectory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


# Set Parameters for timestamps
fontFace = cv2.FONT_HERSHEY_PLAIN
fontScale = 1
thickness = 1
textSize, baseline = cv2.getTextSize("FPS", fontFace, fontScale, thickness)
textOrg = (10, 10 + textSize[1])


# ----------------- FLYING -----------------#
def captureImages(directory):
    # capture image
    raw = client.simGetImage(cameraName, cameraTypeMap[cameraType])
    drone_position = client.simGetVehiclePose().position
    t = Vector3r(drone_position.x_val, drone_position.y_val, drone_position.z_val)
    x_val = "{:.2f}".format(t.x_val)
    y_val = "{:.2f}".format(t.y_val)
    z_val = "{:.2f}".format(t.z_val)
    str_position = 'x:' + x_val + ' ' + 'y: ' + y_val + ' ' + 'z:' + z_val
    if raw is None:
        print("Camera is not returning image, please check airsim for error messages")
        sys.exit(0)
    else:
        png = cv2.imdecode(airsim.string_to_uint8_array(raw), cv2.IMREAD_UNCHANGED)
        img_name = str_position
        cv2.putText(png, img_name, textOrg, fontFace, fontScale, (0, 255, 255), thickness)
        file_name = 'Frame' + datetime.datetime.now().time().strftime("%M-%S") + '.png'
        cv2.imwrite(os.path.join(directory, file_name), png)


def performCycle(velocity, directory):
    for i in range(10):
        # move forward
        client.moveByVelocityAsync(velocity, 0, 0, 2).join()
        captureImages(directory)

    for j in range(3):
        # move left
        client.moveByVelocityAsync(0, -velocity, 0, 1).join()
        captureImages(directory)

    for i in range(10):
        # move forward
        client.moveByVelocityAsync(-velocity, 0, 0, 2).join()
        captureImages(directory)

    for j in range(4):
        # move left
        client.moveByVelocityAsync(0, -velocity, 0, 1).join()
        captureImages(directory)


def performFullPatrol(velocity, directory):
    for i in range(3):
        performCycle(velocity, directory)


def resetPosition():
    client.landAsync().join()
    client.reset()
    client.enableApiControl(False)
    client.enableApiControl(True)
    client.takeoffAsync().join()


def setSegmentationSettings():
    # Grass
    client.simSetSegmentationObjectID("Grass_Floor", 9, True)
    # Landscape
    client.simSetSegmentationObjectID("Landscape_1", 9, True)
    # Bushes
    client.simSetSegmentationObjectID("SM_Bush[\w]*", 4, True)
    # Connectors pipes
    client.simSetSegmentationObjectID("Connector[\w]*", 16, True)
    # T-Connectors pipes
    client.simSetSegmentationObjectID("T_connector[\w]*", 16, True)
    # Straight pipes
    client.simSetSegmentationObjectID("Pipe[\w]*", 16, True)
    # Bases
    client.simSetSegmentationObjectID("Base[\w]*", 16, True)
    # Unions
    client.simSetSegmentationObjectID("Union[\w]*", 16, True)


# connect to the AirSim simulator using Tornado
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
initial_position = client.simGetVehiclePose().position

# take off
client.takeoffAsync().join()
# Fly
cameraName = setCameraName("bottom_center")

# RGB images
cameraType = setCameraType("scene")
rgb_dir = createDirectory("generated-data/RGB")
velocity = 10
performFullPatrol(velocity, rgb_dir)
resetPosition()

# Segmentation map images
cameraType = setCameraType("segmentation")
seg_dir = createDirectory("generated-data/SEG")
setSegmentationSettings()
performFullPatrol(velocity, seg_dir)

# Land Drone
client.landAsync().join()

# Reset Position of Drone
client.reset()

# Disconnect from AirSim
client.enableApiControl(False)
