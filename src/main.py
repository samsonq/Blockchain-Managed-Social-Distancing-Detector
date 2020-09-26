import os
import numpy as np
import cv2
import argparse
import imutils
#import mysql.connector
#from mysql.connector import Error
#from mysql.connector import errorcode
from scipy.spatial import distance
from datetime import datetime
from yolo_config import *
from detector import detect


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
    return vars(ap.parse_args())


def detect_social_distancing(args):
    """
    Runs model to detect social distancing between people in crowds.
    :param args: video feed arguments
    :return: violations
    """
    labels_path = os.path.sep.join([MODEL_PATH, "coco.names"])
    labels = open(labels_path).read().strip().split("\n")

    weights_path = os.path.sep.join([MODEL_PATH, "yolov3.weights"])
    config_path = os.path.sep.join([MODEL_PATH, "yolov3.cfg"])

    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)

    if USE_GPU:
        print("[INFO] setting preferable backend and target to CUDA...")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    vs = cv2.VideoCapture(args["input"] if args["input"] else 0)
    writer = None

    while True:
        # read the next frame from the file
        (grabbed, frame) = vs.read()
        if not grabbed:
            break
        # resize the frame and then detect people (and only people) in it
        frame = imutils.resize(frame, width=700)
        results = detect(frame, net, ln, person_idx=labels.index("person"))
        violate = set()
        if len(results) >= 2:
            # extract centroids from results and compute Euclidean distances between all pairs of centroids
            centroids = np.array([r[2] for r in results])
            dist = distance.cdist(centroids, centroids, metric="euclidean")
            # loop over the upper triangular of the distance matrix
            for i in range(0, dist.shape[0]):
                for j in range(i + 1, dist.shape[1]):
                    if dist[i, j] <= MIN_DISTANCE:
                        violate.add(i)
                        violate.add(j)

        # visualize social distancing
        for (i, (prob, bbox, centroid)) in enumerate(results):
            (startX, startY, endX, endY) = bbox
            (cX, cY) = centroid
            color = (0, 255, 0)
            if i in violate:
                color = (0, 0, 255)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            cv2.circle(frame, (cX, cY), 5, color, 1)
        text = "Social Distancing Violations: {}".format(len(violate))
        cv2.putText(frame, text, (10, frame.shape[0] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 3)

        if args["display"] > 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break  # press q to break

        if args["output"] != "" and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 25, (frame.shape[1], frame.shape[0]), True)

        if writer is not None:
            writer.write(frame)

        #current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        #insert_query = """INSERT INTO Distancing (Location, Local_Time, Violations) VALUES ({}, '{}', {}) """.format(args["location"], current_time, len(violate))
        #cursor = connection.cursor()
        #cursor.execute(insert_query)
    #connection.commit()
    #cursor.close()


def main():
    """
    Runs social distancing detector.
    """
    args = parse_args()
    detect_social_distancing(args)


if __name__ == "__main__":
    """
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='Maxonrow',
                                             user='root',
                                             password='')
    except mysql.connector.Error as error:
        print("Failed to insert record into table {}".format(error))
    """
    main()
