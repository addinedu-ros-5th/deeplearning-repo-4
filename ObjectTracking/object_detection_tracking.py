import os
import numpy as np
import datetime
import cv2
from ultralytics import YOLO

from deep_sort.deep_sort.tracker import Tracker
from deep_sort.deep_sort import nn_matching
from deep_sort.deep_sort.detection import Detection
from deep_sort.tools import generate_detections as gdet

from helper import create_video_writer

# define some parameters
conf_threshold = 0.5
max_cosine_distance = 0.4
nn_budget = None

# Initialize the video capture and the video writer objects
video_path = "/Users/yohan/Desktop/dev_ws/DeepLearning_Project/Object-Detection-and-Tracking-with-YOLOv8-and-DeepSORT/1.mp4"
video_cap = cv2.VideoCapture(video_path)
writer = create_video_writer(video_cap, "/Users/yohan/Desktop/dev_ws/DeepLearning_Project/Object-Detection-and-Tracking-with-YOLOv8-and-DeepSORT/output.mp4")

# Initialize the YOLOv8 model using the default weights
model = YOLO("yolov8n.pt")

# Initialize the deep sort tracker
model_filename = "/Users/yohan/Desktop/dev_ws/DeepLearning_Project/Object-Detection-and-Tracking-with-YOLOv8-and-DeepSORT/config/mars-small128.pb"
encoder = gdet.create_box_encoder(model_filename, batch_size=1)
metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
tracker = Tracker(metric)

# load the COCO class labels the YOLO model was trained on
classes_path = "/Users/yohan/Desktop/dev_ws/DeepLearning_Project/Object-Detection-and-Tracking-with-YOLOv8-and-DeepSORT/config/coco.names"
with open(classes_path, "r") as f:
    class_names = f.read().strip().split("\n")

# create a list of random colors to represent each class
np.random.seed(42)
colors = np.random.randint(0, 255, size=(len(class_names), 3))

# loop over the frames
while True:
    start = datetime.datetime.now()
    ret, frame = video_cap.read()

    if not ret:
        print("End of the video file...")
        break

    results = model(frame)
    for result in results:
        bboxes = []
        confidences = []
        class_ids = []

        for data in result.boxes.data.tolist():
            x1, y1, x2, y2, confidence, class_id = data
            x = int(x1)
            y = int(y1)
            w = int(x2) - int(x1)
            h = int(y2) - int(y1)
            class_id = int(class_id)

            if confidence > conf_threshold:
                bboxes.append([x, y, w, h])
                confidences.append(confidence)
                class_ids.append(class_id)

    names = [class_names[class_id] for class_id in class_ids]
    features = encoder(frame, bboxes)
    dets = [Detection(bbox, conf, class_name, feature) for bbox, conf, class_name, feature in zip(bboxes, confidences, names, features)]

    tracker.predict()
    tracker.update(dets)

    for track in tracker.tracks:
        if not track.is_confirmed() or track.time_since_update > 1:
            continue

        bbox = track.to_tlbr()
        track_id = track.track_id
        class_name = track.get_class()
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        class_id = class_names.index(class_name)
        color = colors[class_id]
        B, G, R = int(color[0]), int(color[1]), int(color[2])

        text = str(track_id) + " - " + class_name
        cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
        cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(text) * 12, y1), (B, G, R), -1)
        cv2.putText(frame, text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
    end = datetime.datetime.now()
    fps = f"FPS: {1 / (end - start).total_seconds():.2f}"
    cv2.putText(frame, fps, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)
    cv2.imshow("Output", frame)
    writer.write(frame)
    if cv2.waitKey(1) == ord("q"):
        break

video_cap.release()
writer.release()
cv2.destroyAllWindows()