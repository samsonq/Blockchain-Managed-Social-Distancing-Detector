import os
import sys
import cv2
import numpy as np
import threading
import imutils
import time
import warnings
import argparse

from detector import Detector
from imutils.video import VideoStream
from flask import Flask, Response, url_for, redirect, render_template
from yolo_config import *
from detector import Detector
from web3 import Web3
warnings.filterwarnings("ignore")

vs = None
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

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

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/7fc9b313b47d488c97c52c3221344c04"))

def update_video(frame_rate):
    # grab global references to the video stream, output frame, and lock variables
    global vs, outputFrame, lock
    
    frame_counter = 0
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


def parse_args():
    """
    Get arguments to run detection model. Input video file to detect social distancing, or
    by default, use webcam for detection.
    :return: program arguments
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=str, default="",
                    help="path to (optional) input video file")
    ap.add_argument("-l", "--location", type=str, default="",
                    help="geo location of video feed")
    ap.add_argument("-o", "--output", type=str, default="",
                    help="path to (optional) output video file")
    ap.add_argument("-d", "--display", type=int, default=1,
                    help="whether or not output frame should be displayed")
    ap.add_argument("-w", "--web", type=int, default=1,
                    help="whether to start the program as a flask web app")
    ap.add_argument("-f", "--frame_rate", type=int, default=60,
                    help="the framerate of the video")
    ap.add_argument("-ip", "--ip", type=str, default="0.0.0.0",
                    help="the ip address")
    ap.add_argument("-p", "--port", type=str, default="8000",
                    help="the port number")
    return vars(ap.parse_args())


def main():
    global vs
    """
    Runs social distancing detector.
    """
    args = parse_args()
    social_distancing_detector = Detector(args["input"], args["output"], args["location"], args["display"])

    if args["web"] == 1:
        # initialize the video stream
        vs = cv2.VideoCapture(args["input"])
        time.sleep(2.0)

        # start a thread that will perform motion detection
        t = threading.Thread(target=update_video, args=(args["frame_rate"],))
        t.daemon = True
        t.start()    # start the flask app
        app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)
    else:
        social_distancing_detector.detect_social_distancing()


if __name__ == "__main__":
    main()

vs.stop()