# import the necessary packages
import base64
import numpy as np
import sys
import time
import cv2
import os

# construct the argument parse and parse the arguments
confthres = 0.6
nmsthres = 0.1


def get_labels(labels_path):
    # load the COCO class labels our YOLO model was trained on
    lpath = os.path.sep.join([yolo_path, labels_path])

    print(yolo_path)
    LABELS = open(lpath).read().strip().split("\n")
    return LABELS


def get_weights(weights_path):
    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join([yolo_path, weights_path])
    print(weightsPath)
    return weightsPath


def get_config(config_path):
    configPath = os.path.sep.join([yolo_path, config_path])
    print(configPath)
    return configPath


def load_model(configpath, weightspath):
    # load our YOLO object detector trained on COCO dataset (80 classes)
    print("[INFO] loading YOLO from disk...")

    try:
        print("Loading config and weights...")
        net = cv2.dnn.readNetFromDarknet(
            configpath, "/tmp/yolov3-tiny.weights")
        print("Model loaded successfully.")
        return net
    except Exception as e:
        print("Failed to load model.")
        print(e)
        return None


def do_prediction(image, net, LABELS):

    (H, W) = image.shape[:2]
    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

    # construct a blob from the input image and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes and
    # associated probabilities
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    # print(layerOutputs)
    end = time.time()

    # show timing information on YOLO
    print("[INFO] YOLO took {:.6f} seconds".format(end - start))

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []
    detected_objects = {}  # Dictionary to store detected objects and their frequencies

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            # print(scores)
            classID = np.argmax(scores)
            # print(classID)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > confthres:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])

                confidences.append(float(confidence))
                classIDs.append(classID)

                # Update the frequency of the detected object
                detected_objects.add(LABELS[classID])

    # apply non-maxima suppression to suppress weak, overlapping bounding boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres,
                            nmsthres)

    # TODO Prepare the output as required to the assignment specification
    # ensure at least one detection exists

    if len(idxs) > 0:
        return detected_objects
    else:
        return None


yolo_path = "/var/task/src/yolo_tiny_configs"

# Yolov3-tiny versrion
current_dir = os.path.dirname(os.path.abspath(__file__))
labelsPath = "coco.names"
cfgpath = "yolov3-tiny.cfg"
wpath = "yolov3-tiny.weights"

Labels = get_labels(labelsPath)
CFG = get_config(cfgpath)
Weights = get_weights(wpath)


def run(encoded_image):
    try:
        img = cv2.imdecode(np.frombuffer(
            base64.b64decode(encoded_image), np.uint8), 1)
        image = np.array(img)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        nets = load_model(CFG, Weights)
        detected_objects = do_prediction(image, nets, Labels)
        return detected_objects

    except Exception as e:

        return f"Exception  {e}"
