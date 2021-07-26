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

person_size = 12
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
NG_count = 0
OK_count = 0
hid = ""

date_old = datetime.date.today()
today = datetime.date.today()

def on_message(client, userdata, msg):
    global keyIn_status, hid, OK_count
    print(msg.topic + " " + msg.payload.decode())
    keyIn_status = 1
    OK_count = OK_count + 1
    hid = msg.payload.decode()

HOST = "localhost"
PORT = 1883
mqtt_topic = "V5F_green" #TOPIC name

client = mqtt.Client()
client.on_message = on_message

client.connect(HOST, PORT, 65535)
client.subscribe(mqtt_topic, qos=0)
client.loop_start()

time_start = time.time()

while True:
    ret, frame = cap.read()
    show_img_o = frame.copy()
    show_img = frame.copy()
    is_person = 0
    if time.time() - time_start > 10:
        time_start = time.time()
        today = datetime.date.today()
        if str(today) != str(date_old):
            date_old = datetime.date.today()
            NG_count = 0
            OK_count = 0
    classes, confidences, boxes = net.detect(frame, confThreshold=0.1, nmsThreshold=0.5)
    if 0 in classes:
        if keyIn_status == 1:
            textColor = (0, 255, 0)
            rectColor = (0, 255, 0)
            cv2.putText(show_img, "OK", (10, 75), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
        else:
            rectColor = (0, 0, 255)
            textColor = (0, 0, 255)
        #person_sum = np.sum(classes == 0)
        if person_status == 1 and video_status == 0:
            video_status = 1
            video_today = datetime.date.today()
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            img_path = "keyIn_video/" + str(video_today) + "/"
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
            pstring = str(int(100 * confidence)) + "%" #信心度
            x_left, y_top, width, height = box
            if (width * height) > (640 * 480) / person_size:
                is_person = 1
                out_count = 0
            if person_status == 0 and is_first == 1 and (width * height) > (640 * 480) / person_size:
                is_first = 0
                #print(x_left + (width / 2))
                if x_left + (width / 2) > (640 / 2):
                    #print("to left")
                    person_in = 0 #由右往左
                    to_left = 1
                    to_right = 0
                else:
                    #print("to right")
                    person_in = 1 #由左往右
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
                        person_in = 1 #由右往左
                    else:
                        print("to right")
                        person_in = 0 #由左往右
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
                    (x_left, y_top), #左上頂點
                    (x_left, y_top + height), #左下頂點
                    (x_left + width, y_top + height), #右下頂點
                    (x_left + width, y_top) #右上頂點
            ]
            
            textCoord = (x_left, y_top - 10) #文字位置
            # 在影像中標出Box邊界和類別、信心度
            cv2.rectangle(show_img, boundingBox[0], boundingBox[2], rectColor, 2)
            cv2.putText(show_img, pstring, textCoord, cv2.FONT_HERSHEY_DUPLEX, 1, rectColor, 2)
        
    if 0 not in classes or is_person == 0:
        out_count = out_count + 1    
        if keyIn_status == 1 and out_count > 10:
            print("OK")
            person_in = 0
            person_status = 0
            person_out = 0
            keyIn_status = 0
            is_first = 1
            if video_status == 1:
                video_status = 0
                out.release()
                hid_video_path = img_path + hid + "/"
                isExist = os.path.exists(hid_video_path)
                if not isExist:
                    os.makedirs(hid_video_path)
                #移動檔案
                os.rename(img_path + now + ".mp4",hid_video_path + now + ".mp4")
        elif person_status == 1 and keyIn_status == 0 and out_count > 10:
            if person_out == 0:
                person_out = 1
                person_out_time = time.time()
            if (time.time() - person_out_time) > 0.5:
                print("NG")
                person_in = 0
                person_status = 0
                person_out = 0
                is_first = 1
                NG_count = NG_count + 1
                if video_status == 1:
                    video_status = 0
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
        elif out_count > 10:
            is_first = 1
            to_left = 0
            to_right = 0
        #    move_pos.clear()
    cv2.putText(show_img, "NG:"+str(NG_count), (525,25), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
    cv2.putText(show_img, "OK:"+str(OK_count), (525,75), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
    if to_left == 1:
        pstring = "Out"
        cv2.putText(show_img, pstring, (10,25), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0), 2)
    elif to_right == 1:
        pstring = "in"
        cv2.putText(show_img, pstring, (10,25), cv2.FONT_HERSHEY_DUPLEX, 1, (255,0,0), 2)
    
    #if video_status == 1:
    #    out.write(show_img)
    cv2.imshow('predict', show_img)
    cv2.imshow('show', show_img_o)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if video_status == 1:
    out.release()
cap.release()


