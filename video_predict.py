import paho.mqtt.client as mqtt
import cv2
import numpy as np
import datetime
import time
import glob
import os

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
fourcc = cv2.VideoWriter_fourcc(*'XVID')

keyIn_status = 0
personIn_time = 0
person_img = 0
person_status = 0
person_out = 0
person_out_time = 0
out_status = 0
out_count = 0
video_status = 0
def on_message(client, userdata, msg):
    global keyIn_status
    print(msg.topic + " " + str(msg.payload))
    if msg.payload.decode()== 'key_in':
        print("key_in")
        keyIn_status = 1
        #client.publish("callback_N1",result,0)

def on_publish(client, userdata, mid):
    print("On onPublish: qos = %d" % mid)

HOST = "192.168.50.224"#"172.20.10.12"
PORT = 1883

client = mqtt.Client()
client.on_message = on_message
client.on_publish = on_publish

client.connect(HOST, PORT, 600)
client.subscribe('keyin_status',qos=0)
client.loop_start()

while True:
    ret, frame = cap.read()
    show_img = frame.copy()
    #frame = cv2.resize(frame, (416,416))
    classes, confidences, boxes = net.detect(frame, confThreshold=0.1, nmsThreshold=0.5)
    if 0 in classes:
        #person_sum = np.sum(classes == 0)
        out_count = 0
        if person_status == 1 and video_status == 0:
            video_status = 1
            today = datetime.date.today()
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            img_path = "not_keyIn_img/" + str(today) + "/"
            isExist = os.path.exists(img_path)
            if not isExist:
                os.makedirs(img_path)
            out = cv2.VideoWriter(img_path + now + ".avi", fourcc, 15.0, (640, 480))
        if video_status == 1:
            out.write(show_img)
        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
            if classId != 0:
                continue
            
            old_confidence = confidence
            pstring = str(int(100 * confidence)) + "%" #信心度
            x_left, y_top, width, height = box

            if person_status == 0 and x_left > (640 / 4) and x_left < (640 / 4) * 3:
                person_status = 1
                #personIn_time = time.time()
            elif person_status == 1:
                x_left, y_top, width, height = box
                if (width * height) > (640 * 480) / 5 * 2:
                    #person_img = frame.copy()
                    pass

            boundingBox = [
                    (x_left, y_top), #左上頂點
                    (x_left, y_top + height), #左下頂點
                    (x_left + width, y_top + height), #右下頂點
                    (x_left + width, y_top) #右上頂點
            ]
            
            #if classId == 0:
            #    rectColor = (255, 0, 0)
            #    textCoord = (x_left, y_top - 10)
            
            rectColor = (0, 0, 255)
            textCoord = (x_left, y_top - 10) #文字位置
            # 在影像中標出Box邊界和類別、信心度
            cv2.rectangle(show_img, boundingBox[0], boundingBox[2], rectColor, 2)
            cv2.putText(show_img, pstring, textCoord, cv2.FONT_HERSHEY_DUPLEX, 1, rectColor, 2)
        
    else:
        out_count = out_count + 1    
        if keyIn_status == 1 and out_count > 3:
            print("OK")
            person_status = 0
            person_out = 0
            keyIn_status = 0
            video_status = 0
            out.release()
            os.remove(img_path + now + ".avi")
        elif person_status == 1 and keyIn_status == 0 and out_count > 3:
            if person_out == 0:
                person_out = 1
                person_out_time = time.time()
            if (time.time() - person_out_time) > 1:
                print("NG")
                person_status = 0
                person_out = 0
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
    cv2.imshow('frame', show_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()


