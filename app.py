#!/usr/bin/env python


import sys
import os
import cv2
import numpy as np
import time
import rospy

from importlib import import_module
from interbotix_xs_modules.locobot import InterbotixLocobotCreate3XS
from flask import Flask, render_template, Response
import pyrealsense2 as rs
from sensor_msgs.msg import Image


locobot = InterbotixLocobotCreate3XS(robot_model="locobot_base")
print("1")
app = Flask(__name__)
print("2")

speed = 0.05
duration = 0.1
@app.route('/go_up')
def go_up():
    print("go up")
    locobot.base.move(x=speed, yaw=0, duration=duration)
    return "nothing"

@app.route('/go_down')
def go_down():
    locobot.base.move(x=-speed, yaw=0, duration=duration)
    print("go_down")
    return "nothing"

@app.route('/go_left')
def go_left():
    locobot.base.move(x=speed, yaw=90, duration=duration)
    print("go_left")
    return "nothing"

@app.route('/go_right')
def go_right():
    locobot.base.move(x=speed, yaw=180, duration=duration)
    print("go right")
    return "nothing"

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    yield b'--frame\r\n'
    while True:
        color_image = locobot.base.get_img()
        color_image = np.array(color_image)
        _, frame = cv2.imencode('.jpeg', color_image)
        frame = frame.tobytes()
        # time.sleep(0.05)
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
print("3")

if __name__ == '__main__':
    print("4")

    print("before")
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 1234)), debug=True)
    print("after")
