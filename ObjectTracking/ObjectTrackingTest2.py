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

# Parameter definition
conf_threshold = 0.5
max_cosine_distance = 0.4
nn_budget = None
TIME_WINDOW = 2  # time 2 seconds

# Initialize the video capture and the video writer objects
video_cap = cv2.VideoCapture(0)  # webcam use
video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video_cap.set(cv2.CAP_PROP_FPS, 15)  # webcam FPS set

# Initialize the YOLOv8 model using the default weights
model = YOLO("/Users/yohan/Desktop/dev_ws/DeepLearning_Project/Object-Detection-and-Tracking-with-YOLOv8-and-DeepSORT/yolov8n.pt")

# Initialize the deep sort tracker
model_filename = "/Users/yohan/Desktop/dev_ws/DeepLearning_Project/Object-Detection-and-Tracking-with-YOLOv8-and-DeepSORT/config/mars-small128.pb"
encoder = gdet.create_box_encoder(model_filename, batch_size=1)
metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
tracker = Tracker(metric)

# Load the COCO class labels the YOLO model was trained on
classes_path = "/Users/yohan/Desktop/dev_ws/DeepLearning_Project/Object-Detection-and-Tracking-with-YOLOv8-and-DeepSORT/config/coco.names"
with open(classes_path, "r") as f:
    class_names = f.read().strip().split("\n")

# Create random colors list
np.random.seed(42)
colors = np.random.randint(0, 255, size=(len(class_names), 3))

# Initialize previous positions dictionary
previous_positions = {}

# Definition of object detection function
def detect_objects(frame):
    results = model(frame)[0]  # Yolov8 called
    boxes = results.boxes.xyxy.cpu().numpy()  # Extract bounding box information
    confidences = results.boxes.conf.cpu().numpy()
    class_ids = results.boxes.cls.cpu().numpy() if hasattr(results.boxes, 'cls') else np.zeros(len(boxes))  # Extract class ID information
    detections = np.concatenate((boxes, confidences[:, np.newaxis], class_ids[:, np.newaxis]), axis=1)  # Detections information concatenate
    return detections

# Definition of calculate speed and direction
def calculate_speed_and_direction(prev_pos, current_pos, time_interval):
    dx = current_pos[0] - prev_pos[0]
    dy = current_pos[1] - prev_pos[1]
    distance = np.sqrt(dx ** 2 + dy ** 2)  # Use the Pythagorean theorem
    speed = distance / time_interval
    direction = np.arctan2(dy, dx) * 180 / np.pi  # in degrees
    return speed, direction

# Define a function and Save current time
def draw_arrow_and_trajectory(frame, obj_id, center_bottom_x, center_bottom_y, prev_bottom_pos):
    current_time = datetime.datetime.now().timestamp()

    # Initialize if object ID is not in previous positions
    if obj_id not in previous_positions:
        previous_positions[obj_id] = []

    positions_list = previous_positions[obj_id]

    # Append the current position and timestamp
    if prev_bottom_pos:
        positions_list.append((prev_bottom_pos, current_time))

        # Remove positions older than TIME_WINDOW seconds
        positions_list = [(pos, ts) for pos, ts in positions_list if current_time - ts <= TIME_WINDOW]

        # Draw a trajectory
        for i in range(1, len(positions_list)):
            cv2.line(frame, (int(positions_list[i - 1][0][0]), int(positions_list[i - 1][0][1])),
                     (int(positions_list[i][0][0]), int(positions_list[i][0][1])), (0, 255, 0), thickness=2)

        cv2.arrowedLine(frame, (int(prev_bottom_pos[0]), int(prev_bottom_pos[1])),
                        (int(center_bottom_x), int(center_bottom_y)), (255, 0, 0), thickness=2, tipLength=0.1)

    previous_positions[obj_id] = positions_list # Update previous positions

# Loop over the frames
while True:
    start = datetime.datetime.now()
    ret, frame = video_cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Frame size
    frame = cv2.resize(frame, (640, 480))

    detections = detect_objects(frame)

    # Reset
    bboxes = []
    confidences = []
    class_ids = []

    # Extract detection object information
    for detection in detections:
        x1, y1, x2, y2, confidence, class_id = detection # Calculate the coordinates and size of the bounding box
        x = int(x1)
        y = int(y1)
        w = int(x2) - int(x1)
        h = int(y2) - int(y1)
        class_id = int(class_id)

        if confidence > conf_threshold:
            bboxes.append([x, y, w, h])
            confidences.append(confidence)
            class_ids.append(class_id)

    # Feature extraction
    names = [class_names[class_id] for class_id in class_ids]
    features = encoder(frame, bboxes)
    dets = [Detection(bbox, conf, class_name, feature) for bbox, conf, class_name, feature in zip(bboxes, confidences, names, features)]

    tracker.predict()
    tracker.update(dets)

    for track in tracker.tracks:
        if not track.is_confirmed() or track.time_since_update > 1:
            continue

        # Track information extraction
        bbox = track.to_tlbr()
        track_id = track.track_id
        class_name = track.get_class()
        # Bounding box coordinate and clor setting
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        class_id = class_names.index(class_name)
        color = colors[class_id]
        B, G, R = int(color[0]), int(color[1]), int(color[2])

        text = str(track_id) + " - " + class_name
        cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
        cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(text) * 12, y1), (B, G, R), -1)
        cv2.putText(frame, text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Speed and direction calculation(Center point corrdinate)
        center_bottom_x = (x1 + x2) / 2
        center_bottom_y = y2  # Bottom center coordinate of bounding box
        current_bottom_pos = (center_bottom_x, center_bottom_y)

        if track_id in previous_positions:
            prev_bottom_pos, prev_time = previous_positions[track_id][-1]  # Get previous possitions
            if isinstance(prev_time, datetime.datetime):
                prev_time = prev_time.timestamp()  # Convert prev_time to timestamp
            time_interval = (start.timestamp() - prev_time) # Time interval calculation
            speed, direction = calculate_speed_and_direction(prev_bottom_pos, current_bottom_pos, time_interval)
            # Text
            speed_text = f"Speed: {speed:.2f}"
            direction_text = f"Direction: {direction:.2f}°"
            cv2.putText(frame, speed_text, (x1 + 5, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, direction_text, (x1 + 5, y1 - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Draw a trajectory
        prev_bottom_pos = previous_positions[track_id][-1][0] if track_id in previous_positions and previous_positions[track_id] else None
        draw_arrow_and_trajectory(frame, track_id, center_bottom_x, center_bottom_y, prev_bottom_pos)

        previous_positions[track_id].append((current_bottom_pos, start.timestamp()))  # Convert the current time to a timstamp and save it

    end = datetime.datetime.now()
    fps = f"FPS: {1 / (end - start).total_seconds():.2f}"
    cv2.putText(frame, fps, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)
    cv2.imshow("Output", frame)
    if cv2.waitKey(1) == ord("q"):
        break

video_cap.release()
cv2.destroyAllWindows()
