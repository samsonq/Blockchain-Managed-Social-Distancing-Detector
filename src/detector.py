import numpy as np
import cv2
from yolo_config import NMS_THRESH, MIN_CONF


def detect(frame, net, ln, person_idx=0):
    """
    Detects people within frames of inputted video.
    :param frame: frame from your video file or directly from webcam
    :param net: pre-initialized and pre-trained YOLO object detection model
    :param ln: YOLO CNN output layer names
    :param person_idx: YOLO class to detect people
    :return:
    """
    (h, w) = frame.shape[:2]
    results = []
    boxes = []
    centroids = []
    confidences = []

    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(ln)

    for output in layer_outputs:
        for detection in output:
            scores = detection[:5]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if class_id == person_idx and confidence >= MIN_CONF:
                box = detection[0:4]*np.array([w, h, w, h])
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
