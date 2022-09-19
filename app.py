#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

app = Flask(__name__)

@app.route('/go_up')
def go_up():
    print("go up")
    return "nothing"

@app.route('/go_down')
def go_down():
    print("go_down")
    return "nothing"

@app.route('/go_left')
def go_left():
    print("go_left")
    return "nothing"

@app.route('/go_right')
def go_right():
    print("go right")
    return "nothing"

# @app.route('/my_action2')
# def go_down():
#   return

# @app.route('/my_action3')
# def go_right():
#   return

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 4444)))
