import paho.mqtt.client as mqtt
import cv2
import numpy as np
import datetime
import time
import glob
import os
#from collections import deque

net = cv2.dnn_DetectionModel('cfg/yolov4-tiny.cfg', 'model/yolov4-tiny.weights')
#net = cv2.dnn_DetectionModel('cfg/enet-coco.cfg', 'model/enetb0-coco_final.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
net.setInputSize(416, 416)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

person_size = 5
keyIn_status = 0
personIn_time = 0
person_img = 0
person_status = 0
person_in = 0
person_out = 0
person_out_time = 0
out_status = 0
out_count = 0
video_status = 0
#move_pos = deque(maxlen=60)
move_count = 0
is_first = 1
to_left = 0
to_right = 0
textColor = (255, 0, 0)
is_person = 0
hid = ""
def on_message(client, userdata, msg):
    global keyIn_status, hid
    print(msg.topic + " " + msg.payload.decode())
    keyIn_status = 1
    hid = msg.payload.decode()

HOST = "localhost"
PORT = 1883
mqtt_topic = "V5F_green" #TOPIC name

client = mqtt.Client()
client.on_message = on_message

client.connect(HOST, PORT, 600)
client.subscribe(mqtt_topic, qos=0)
client.loop_start()

while True:
    ret, frame = cap.read()
    show_img = frame.copy()
    is_person = 0
    classes, confidences, boxes = net.detect(frame, confThreshold=0.1, nmsThreshold=0.5)
    if 0 in classes:
        if keyIn_status == 1:
            cv2.putText(show_img, "OK", (10, 75), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
        #person_sum = np.sum(classes == 0)
        if person_status == 1 and video_status == 0:
            video_status = 1
            today = datetime.date.today()
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            img_path = "keyIn_video/" + str(today) + "/"
            isExist = os.path.exists(img_path)
            if not isExist:
                os.makedirs(img_path)
            out = cv2.VideoWriter(img_path + now + ".mp4", fourcc, 12.0, (640, 480))
        if video_status == 1:
            out.write(show_img)
        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
            if classId != 0:
                continue
            
            old_confidence = confidence
            pstring = str(int(100 * confidence)) + "%" #?????????
            x_left, y_top, width, height = box
            if (width * height) > (640 * 480) / person_size:
                is_person = 1
                out_count = 0
            if person_status == 0 and is_first == 1 and (width * height) > (640 * 480) / person_size:
                is_first = 0
                print(x_left + (width / 2))
                if x_left + (width / 2) > (640 / 2):
                    print("to left")
                    person_in = 1 #????????????
                    to_left = 1
                    to_right = 0
                else:
                    print("to right")
                    person_in = 0 #????????????
                    to_left = 0
                    to_right = 1
            
                
            '''
            if person_status == 0 and (width * height) > (640 * 480) / 10:
                move_pos.append(x_left + (width / 2))
                move_count = move_count + 1
                if move_count == 5:
                    move_count = 0
                    if move_pos[0] - move_pos[len(move_pos) - 1] > 0:
                        print("to left")
                        person_in = 1 #????????????
                    else:
                        print("to right")
                        person_in = 0 #????????????
                    move_pos.clear()
            '''
            if person_status == 0 and person_in == 1: #and x_left > (640 / 4) and x_left < (640 / 4) * 3 and (width * height) > (640 * 480) / 5:
                person_status = 1
            #elif person_status == 1:
            #    x_left, y_top, width, height = box
            #    if (width * height) > (640 * 480) / 5 * 2:
            #        #person_img = frame.copy()
            #        pass

            boundingBox = [
                    (x_left, y_top), #????????????
                    (x_left, y_top + height), #????????????
                    (x_left + width, y_top + height), #????????????
                    (x_left + width, y_top) #????????????
            ]
            
            rectColor = (0, 0, 255)
            textCoord = (x_left, y_top - 10) #????????????
            # ??????????????????Box???????????????????????????
            cv2.rectangle(show_img, boundingBox[0], boundingBox[2], rectColor, 2)
            cv2.putText(show_img, pstring, textCoord, cv2.FONT_HERSHEY_DUPLEX, 1, rectColor, 2)
        
    if 0 not in classes or is_person == 0:
        out_count = out_count + 1    
        if keyIn_status == 1 and out_count > 3:
            print("OK")
            person_in = 0
            person_status = 0
            person_out = 0
            keyIn_status = 0
            video_status = 0
            is_first = 1
            out.release()
            hid_video_path = img_path + hid + "/"
            isExist = os.path.exists(hid_video_path)
            if not isExist:
                os.makedirs(hid_video_path)
            #????????????
            os.rename(img_path + now + ".mp4",hid_video_path + now + ".mp4")
        elif person_status == 1 and keyIn_status == 0 and out_count > 3:
            if person_out == 0:
                person_out = 1
                person_out_time = time.time()
            if (time.time() - person_out_time) > 0.5:
                print("NG")
                person_in = 0
                person_status = 0
                person_out = 0
                video_status = 0
                is_first = 1
                out.release()
                '''
                today = datetime.date.today()
                now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                img_path = "not_keyIn_img/" + str(today) + "/"
                isExist = os.path.exists(img_path)
                if not isExist:
                    os.makedirs(img_path)
                cv2.imwrite(img_path + now + ".jpg", person_img)
                print(img_path + now + ".jpg")
                cv2.imshow('NG', person_img)
                '''
        elif out_count > 3:
            is_first = 1
            to_left = 0
            to_right = 0
        #    move_pos.clear()
    if to_left == 1:
        pstring = "To Left"
        cv2.putText(show_img, pstring, (10,25), cv2.FONT_HERSHEY_DUPLEX, 1, textColor, 2)
    elif to_right == 1:
        pstring = "To Right"
        cv2.putText(show_img, pstring, (10,25), cv2.FONT_HERSHEY_DUPLEX, 1, textColor, 2)
    #if video_status == 1:
    #    out.write(show_img)
    cv2.imshow('frame', show_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#out.release()
cap.release()


