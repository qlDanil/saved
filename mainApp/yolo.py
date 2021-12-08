import os
import cv2
from yolov4.tflite import YOLOv4


def get_items(url):
    url = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + url

    yolo = YOLOv4()
    yolo.config.parse_names("mainApp/yolov4Data/coco.names")
    yolo.config.parse_cfg("mainApp/yolov4Data/yolov4-tiny.cfg")
    yolo.load_tflite("mainApp/yolov4Data/yolov4-tiny-float16.tflite")

    frame = cv2.imread(url)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    bboxes = yolo.predict(frame_rgb, prob_thresh=0.25)
    import time
    time.sleep(30)
    items = set()
    for box in bboxes:
        items.add(yolo.config.names[box[4]])

    return list(items)
