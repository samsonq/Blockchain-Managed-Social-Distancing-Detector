import os
import sys
import numpy as np
import cv2
import imutils
from scipy.spatial import distance
from yolo_config import MODEL_PATH, NMS_THRESH, USE_GPU, min_conf, min_distance
from datetime import datetime
from on_chain import OnChain
from off_chain import OffChain


class Detector:

    def __init__(self, vid_input, vid_output, location, display):
        self.vid_input = vid_input
        self.vid_output = vid_output
        self.location = location
        self.display = display
        self.vs = cv2.VideoCapture(self.vid_input if self.vid_input else 0)
        
        labels_path = os.path.sep.join([MODEL_PATH, "coco.names"])
        self.labels = open(labels_path).read().strip().split("\n")

        weights_path = os.path.sep.join([MODEL_PATH, "yolov3.weights"])
        config_path = os.path.sep.join([MODEL_PATH, "yolov3.cfg"])

        self.net = cv2.dnn.readNetFromDarknet(config_path, weights_path)

        if USE_GPU:
            print("[INFO] setting preferable backend and target to CUDA...")
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        ln = self.net.getLayerNames()
        self.ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        self.off_chain = OffChain()
        self.on_chain = OnChain()

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
                if class_id == person_idx and confidence >= min_conf[0]:
                    box = detection[0:4] * np.array([w, h, w, h])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    centroids.append((centerX, centerY))
                    confidences.append(float(confidence))

        ids = cv2.dnn.NMSBoxes(boxes, confidences, min_conf[0], NMS_THRESH)
        if len(ids) > 0:
            for i in ids.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                r = (confidences[i], (x, y, x + w, y + h), centroids[i])
                results.append(r)
        return results

    def detect_violations(self):
        violate = set()
        (grabbed, frame) = self.vs.read()
        if not grabbed:
            return grabbed, frame, violate
        frame = imutils.resize(frame, width=700)
        results = Detector.detect(frame, self.net, self.ln, person_idx=self.labels.index("person"))
        
        if len(results) >= 2:
            centroids = np.array([r[2] for r in results])
            dist = distance.cdist(centroids, centroids, metric="euclidean")
            for i in range(0, dist.shape[0]):
                for j in range(i + 1, dist.shape[1]):
                    if dist[i, j] <= min_distance[0]:
                        violate.add(i)
                        violate.add(j)

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

        self.store_event(len(violate))  # Store event on and off chain
        return grabbed, frame, violate

    def detect_social_distancing(self):
        """
        Runs model to detect social distancing between people in crowds.
        """
        writer = None

        while True:
            (grabbed, frame, violate) = self.detect_violations()
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

            self.store_event(len(violate))  # Store event on and off chain

        self.off_chain.close_connection()
        return

    def store_event(self, violations):
        """
        Stores event information off-chain and hash of event information on-chain.
        :param violations: number of violations
        """
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        insert_query = """INSERT INTO social_distancing (Location, Local_Time, Violations) VALUES ('{}', '{}', {})""".format(self.location, current_time, violations)
        self.off_chain.insert(insert_query)

        event_id = self.off_chain.select("""SELECT LAST_INSERT_ID() FROM social_distancing""")[0][0]
        self.on_chain.store_hash(event_id, self.location, current_time, violations)
