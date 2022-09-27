#!/usr/bin/env python


import sys
import os
import cv2
import numpy as np
import time

from importlib import import_module
from interbotix_xs_modules.locobot import InterbotixLocobotCreate3XS
from flask import Flask, render_template, Response
import pyrealsense2 as rs
from subscriber import listener
from sensor_msgs.msg import Image

# sys.path.insert(0, '/home/amninder/Desktop/Folder_2')
app = Flask(__name__)

#manually initialize the camera stuff
def init_pipeline():
    # cam = Camera()
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)


#robot api initialization
# locobot = InterbotixLocobotCreate3XS(robot_model="locobot_base")
speed = 0.25








@app.route('/go_up')
def go_up():
    print("go up")
    locobot.base.move(x=speed, yaw=0, duration=1.0)
    return "nothing"

@app.route('/go_down')
def go_down():
    locobot.base.move(x=-speed, yaw=0, duration=1.0)
    print("go_down")
    return "nothing"

@app.route('/go_left')
def go_left():
    locobot.base.move(x=speed, yaw=90, duration=1.0)
    print("go_left")
    return "nothing"

@app.route('/go_right')
def go_right():
    locobot.base.move(x=-speed, yaw=90, duration=1.0)
    print("go right")
    return "nothing"

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def callback():
    yield b'--frame\r\n'
    time.sleep(0.05)
    yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'

    
def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("/locobot/camera/color/image_raw", Image, callback)
    rospy.spin()




    
def gen():
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        #  Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))
        # print(type(images))
        # for image in images:
        # print(type(image))
        _, frame = cv2.imencode('.jpeg', color_image)
        frame = frame.tobytes()
        time.sleep(0.05)
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(callback(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    listener()
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 4444)))
