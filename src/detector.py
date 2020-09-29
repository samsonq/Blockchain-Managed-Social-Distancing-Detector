import os
import sys
import numpy as np
import cv2
import imutils
from scipy.spatial import distance
from yolo_config import *
from datetime import datetime
from hashlib import sha256
from on_chain import OnChain
from off_chain import OffChain


class Detector:

    def __init__(self, vid_input, vid_output, location, display):
        self.vid_input = vid_input
        self.vid_output = vid_output
        self.location = location
        self.display = display
        #self.off_chain = OffChain()
        #self.on_chain = OnChain()

    @staticmethod
    def detect(frame, net, ln, person_idx=0):
        """
        Detects people within frames of inputted video.
        :param frame: frame from your video file or directly from webcam
        :param net: pre-initialized and pre-trained YOLO object detection model
        :param ln: YOLO CNN output layer names
        :param person_idx: YOLO class to detect people
        :return: detection locations and confidence levels
        """
        (h, w) = frame.shape[:2]
        results = []
        boxes = []
        centroids = []
        confidences = []

        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layer_outputs = net.forward(ln)

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if class_id == person_idx and confidence >= MIN_CONF:
                    box = detection[0:4] * np.array([w, h, w, h])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    centroids.append((centerX, centerY))
                    confidences.append(float(confidence))

        ids = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONF, NMS_THRESH)
        if len(ids) > 0:
            for i in ids.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                r = (confidences[i], (x, y, x + w, y + h), centroids[i])
                results.append(r)
        return results

    def detect_violations(self, vs, net, ln, labels):
        violate = set()
        # read the next frame from the file
        (grabbed, frame) = vs.read()
        if not grabbed:
            return (grabbed, frame, violate)
        # resize the frame and then detect people (and only people) in it
        frame = imutils.resize(frame, width=700)
        results = Detector.detect(frame, net, ln, person_idx=labels.index("person"))
        
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
        return (grabbed, frame, violate)

    def detect_social_distancing(self):
        """
        Runs model to detect social distancing between people in crowds.
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

        vs = cv2.VideoCapture(self.vid_input if self.vid_input else 0)
        writer = None

        while True:
            (grabbed, frame, violate)  = self.detect_violations(vs, net, ln, labels)
            if not grabbed:
                break

            if self.display > 0:
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break  # press q to break

            if self.vid_output != "" and writer is None:
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                writer = cv2.VideoWriter(self.vid_output, fourcc, 25, (frame.shape[1], frame.shape[0]), True)

            if writer is not None:
                writer.write(frame)


            # On/Off chain stuff #
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            insert_query = """INSERT INTO Distancing (Location, Local_Time, Violations) VALUES ({}, '{}', {})""".format(self.location, current_time, len(violate))
            #self.off_chain.insert(insert_query)

            select_query = """SELECT """
            #event = self.off_chain.select(select_query)

            #event_str = event[0][0] + self.location + current_time + len(violate)
            #event_hash = sha256(event_str.encode()).hexdigest()
        # connection.commit()
        # cursor.close()
