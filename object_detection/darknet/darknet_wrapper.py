import os
from typing import List

import cv2
from shapely.geometry import Point

from object_detection.bounding_box import BoundingBox
from object_detection.darknet import darknet
from object_detection.object_detector.object_detector_result import DetectedObject, DetectedObjectType, Distance


def _load_meta_path():
    meta_path = "/home/manuel/PREN/workspaces/informatik/object_detection/darknet/obj_both.data"
    if not os.path.exists(meta_path):
        raise ValueError("Invalid data file path `" + os.path.abspath(meta_path) + "`")
    return meta_path


def _load_weight_path():
    weight_path = "/home/manuel/PREN/workspaces/informatik/object_detection/darknet/weights/yolov3-tiny_3l_8000_both.weights"
    if not os.path.exists(weight_path):
        raise ValueError("Invalid weight path `" + os.path.abspath(weight_path) + "`")
    return weight_path


def _load_config_path():
    config_path = "/home/manuel/PREN/workspaces/informatik/object_detection/darknet/yolov3-tiny_3l_both.cfg"
    if not os.path.exists(config_path):
        raise ValueError("Invalid config path `" + os.path.abspath(config_path) + "`")
    return config_path


def _create_detected_objects_for_pylons(detections) -> List[DetectedObject]:
    detected_objects = []
    for detection in detections:
        if "trafficcone" == detection[0].decode():
            probability: int = round(detection[1] * 100, 2)
            bounding_box: BoundingBox = _create_bounding_box(detection)
            detected_object = DetectedObject(DetectedObjectType.Pylon, bounding_box, Distance(-1, False), probability)
            detected_objects.append(detected_object)
    return detected_objects


def _create_detected_objects_for_obstacle(detections) -> List[DetectedObject]:
    detected_objects = []
    for detection in detections:
        if "squaretimber" == detection[0].decode():
            probability: int = round(detection[1] * 100, 2)
            bounding_box: BoundingBox = _create_bounding_box(detection)
            detected_object = DetectedObject(DetectedObjectType.SquareTimber, bounding_box, Distance(-1, False),
                                             probability)
            detected_objects.append(detected_object)
    return detected_objects


def _create_bounding_box(detection) -> BoundingBox:
    rectangle_center_point: Point = Point(detection[2][0], detection[2][1])
    width = detection[2][2]
    height = detection[2][3]
    return BoundingBox.of_rectangle_by_center(rectangle_center_point, width, height)


class DarknetWrapper:

    def __init__(self):
        self._config_path = _load_config_path()
        self._weight_path = _load_weight_path()
        self._meta_path = _load_meta_path()
        self._net_main = self._load_net_main()
        self._meta_main = self._load_meta_main()
        self._alt_names = self._load_alt_names()
        # Create an image we reuse for each detect
        self._darknet_image = darknet.make_image(darknet.network_width(self._net_main),
                                                 darknet.network_height(self._net_main), 3)

    def _load_net_main(self):
        return darknet.load_net_custom(self._config_path.encode("ascii"), self._weight_path.encode("ascii"), 0, 1)

    def _load_meta_main(self):
        return darknet.load_meta(self._meta_path.encode("ascii"))

    def _load_alt_names(self):
        try:
            with open(self._meta_path) as metaFH:
                meta_contents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", meta_contents, re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            return [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass
        return None

    def detect_pylons(self, frame) -> List[DetectedObject]:
        self._initialize_darknet_image(frame)
        detections = darknet.detect_image(self._net_main, self._meta_main, self._darknet_image, thresh=0.25)
        return _create_detected_objects_for_pylons(detections)

    def detect_obstacles(self, frame) -> List[DetectedObject]:
        self._initialize_darknet_image(frame)
        detections = darknet.detect_image(self._net_main, self._meta_main, self._darknet_image, thresh=0.25)
        return _create_detected_objects_for_obstacle(detections)

    def _initialize_darknet_image(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(self._net_main),
                                    darknet.network_height(self._net_main)),
                                   interpolation=cv2.INTER_LINEAR)
        darknet.copy_image_from_bytes(self._darknet_image, frame_resized.tobytes())
