"""
Configurations for YOLO model.
"""

MODEL_PATH = "yolo-coco"
NMS_THRESH = 0.3
USE_GPU = True  # NVIDIA GPU usage for inference

min_conf = [0.9]  # minimum confidence level
min_distance = [50]  # minimum social distancing distance
