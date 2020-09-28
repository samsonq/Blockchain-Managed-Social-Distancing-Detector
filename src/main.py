import os
import sys
import numpy as np
import warnings
import argparse
from yolo_config import *
from detector import Detector
from web3 import Web3
warnings.filterwarnings("ignore")

web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/7fc9b313b47d488c97c52c3221344c04"))


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


def main():
    """
    Runs social distancing detector.
    """
    args = parse_args()
    social_distancing_detector = Detector(args["input"], args["output"], args["location"], args["display"])
    social_distancing_detector.detect_social_distancing()


if __name__ == "__main__":
    main()
