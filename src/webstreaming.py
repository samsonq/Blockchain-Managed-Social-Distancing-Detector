import numpy as np
import cv2
import threading
import argparse
import imutils
import time
import cv2
import warnings
from detector import Detector
from imutils.video import VideoStream
from flask import Flask, Response, url_for, redirect, render_template
from yolo_config import *
warnings.filterwarnings("ignore")

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream
vs = cv2.VideoCapture("static/test.mp4")
time.sleep(2.0)

@app.route("/")
def index():
    return redirect(url_for("video_face_tracking"))

@app.route("/set_confidence/<confidence>", methods=['POST'])
def set_confidence(confidence):
    MIN_CONF = confidence

@app.route("/set_min_distance/<distance>", methods=['POST'])
def set_min_distance(distance):
    MIN_DISTANCE = distance

@app.route("/video_face_tracking")
def video_face_tracking():
    return render_template("videoFaceTracking.html")

def update_video(frameCount):
    # grab global references to the video stream, output frame, and lock variables
    global vs, outputFrame, lock
    
    frame_counter = 0
    frame_rate = 100
    prev = 0

    social_distancing_detector = Detector(0, 0, "location", 0)

    # loop over frames from the video stream
    while True:
        time_elapsed = time.time() - prev
        if time_elapsed > 1./frame_rate:
            prev = time.time()

            #If the last frame is reached, reset the capture and the frame_counter
            frame_counter += 1
            if frame_counter >= int(vs.get(cv2.CAP_PROP_FRAME_COUNT)) - 10:
                frame_counter = 0 #Or whatever as long as it is the same as next line
                vs.set(cv2.CAP_PROP_POS_FRAMES, 0)

            (grabbed, frame, violate) = social_distancing_detector.detect_violations()
            if not grabbed:
                break

            # acquire the lock, set the output frame, and release the lock
            with lock:
                outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True, help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32, help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    # start a thread that will perform motion detection
    t = threading.Thread(target=update_video, args=(args["frame_count"],))
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()
