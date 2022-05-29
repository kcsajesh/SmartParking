import cv2 as cv
import pickle
import pyrebase
import numpy as np
import threading

from time import sleep
from datetime import datetime

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

firebaseConfig = {"apiKey": "AIzaSyC8RUtE7A5yrBGHewTqqJvlMJ06He0xNBQ",
  "authDomain": "smart-parking-69f14.firebaseapp.com",
  "databaseURL": "https://smart-parking-69f14-default-rtdb.firebaseio.com",
  "projectId": "smart-parking-69f14",
  "storageBucket": "smart-parking-69f14.appspot.com",
  "messagingSenderId": "557461183636",
  "appId": "1:557461183636:web:6cf6db48f98d8ba16a6881",
  "measurementId": "G-1LMP3N5VMM"
}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

data = {
"slot0":"[\"1\",\"0\",\"NA\",\"00:00:00\",\"00:00:00\",\"00:00:00\",\"NA\"]",
"slot1":"[\"1\",\"0\",\"NA\",\"00:00:00\",\"00:00:00\",\"00:00:00\",\"NA\"]",
"slot2":"[\"1\",\"0\",\"NA\",\"00:00:00\",\"00:00:00\",\"00:00:00\",\"NA\"]",
"slot3":"[\"1\",\"0\",\"NA\",\"00:00:00\",\"00:00:00\",\"00:00:00\",\"NA\"]",
"slot4":"[\"1\",\"0\",\"NA\",\"00:00:00\",\"00:00:00\",\"00:00:00\",\"NA\"]",
"slot5":"[\"1\",\"0\",\"NA\",\"00:00:00\",\"00:00:00\",\"00:00:00\",\"NA\"]"
}
db.child("SlotInfo").set(data)

#code for led lights
slot0,slot1,slot2,slot3,slot4,slot5 = 11,13,15,16,18,22
led_list = [11,13,15,16,18,22]
GPIO.setup(slot0,GPIO.OUT)
GPIO.setup(slot1,GPIO.OUT)
GPIO.setup(slot2,GPIO.OUT)
GPIO.setup(slot3,GPIO.OUT)
GPIO.setup(slot4,GPIO.OUT)
GPIO.setup(slot5,GPIO.OUT)

#for servo motor

#GPIO.setup(7,GPIO.OUT)
#p = GPIO.PWM(7,50)
#p.start(7.5)

cap = cv.VideoCapture(0)

entered_code = []
duration = {}

firebase_result = db.child("Parking4").get()
dict_result = firebase_result.val()
results = list(dict_result.items())
unique_no=[]
for i in range(len(results)):
    a=results[i][1]
    unique_no.append(a[-7:-2])

def calculate_cost(duration_time_data):
    seconds = duration_time_data.total_seconds()
    return (seconds % 3600) // 60



def entry_check(code):
    print('Give Access to enter')
    entered_code.append(code)
    entry = datetime.now()
    entry_time = entry.strftime('%H:%M:%S')
    duration.update({code: entry_time})
    #p.ChangeDutyCycle(2.5)
    #sleep(0.5)
    #p.ChangeDutyCycle(7.5)
    #sleep(0.5)
    #print(duration)
    print("Entry")


def exit_check(code):
    print('give access to exit')
    entry_time_at_exit = duration.get(code)
    exit = datetime.now()
    exit_time = exit.strftime('%H:%M:%S')
    duration_time = datetime.strptime(exit_time, '%H:%M:%S') - datetime.strptime(entry_time_at_exit, '%H:%M:%S')
    duration.pop(code)
    print(duration_time)
    entered_code.remove(code)
    total_cost = calculate_cost(duration_time)
    #p.ChangeDutyCycle(2.5)
    #sleep(0.5)
    #p.ChangeDutyCycle(7.5)
    #sleep(0.5)
    print(f"Your total cost is {total_cost}")
    print()

def get_input():
	get_data = input("Enter code:: ")
	if get_data in unique_no and get_data not in entered_code:
		entry_check(get_data)

	elif get_data in unique_no and get_data in entered_code:
		exit_check(get_data)
	print(entered_code)
	return get_data

def checkParkingSpace(imgPro):
	spaceCounter = 0
	for i,pos in enumerate(posList):
		x,y = pos
		imgCrop = imgPro[y:y+height,x:x+width]
		#cv.imshow(str(x*y),imgCrop)
		count = cv.countNonZero(imgCrop)
		slot = "slot"
		firebase_result = db.child("SlotInfo").child("{}{}".format(slot,i)).get()
		result = firebase_result.val()
		entry = "00:00:00"
		exit = "00:00:00"

		if count<4000:
			color=(0,250,0)
			thickness = 3
			spaceCounter += 1
			if (result[6]=='0'):
				GPIO.output(led_list[i],True)
				db.child("SlotInfo").update({"{}{}".format(slot,i):"[\"1\",\"0\",\"NA\",\"00:00:00\",\"00:00:00\",\"00:00:00\",\"NA\"]"})
			else:
				GPIO.output(led_list[i],False)
				color=(255,0,255)
				spaceCounter -= 1

		else:
			color = (0,0,255)
			thickness = 3
			now= datetime.now()
			entry = now.strftime("%H:%M:%S")
			datas = "[\"0\",\"0\",\"NA\",\"{}\",\"00:00:00\",\"00:00:00\",\"NA\"]".format(entry)
			db.child("SlotInfo").update({"{}{}".format(slot,i):"[\"0\",\"0\",\"NA\",\"{}\",\"00:00:00\",\"00:00:00\",\"NA\"]".format(entry)})

			if (result[6]=='0'):
				GPIO.output(led_list[i],False)
		cv.rectangle(ims,pos,(pos[0]+width,pos[1]+height),color,thickness)
		cv.putText(ims,str(count),(x,y+15),1,1,color,2)
		cv.putText(ims,str(i),(x+15,y+45),1,2,(255,0,0),2)

	cv.putText(ims,f'Free:{spaceCounter}/{len(posList)}',(10,45),3,1,(255,0,0),2)



with open('CarParkPos','rb') as f:
                posList = pickle.load(f)

width,height = 168,335

try :
	while True:
		success,img = cap.read()
		ims = cv.resize(img, (720, 640)) 

		imgGray = cv.cvtColor(ims,cv.COLOR_BGR2GRAY)
		imgBlur = cv.GaussianBlur(imgGray,(3,3),1)
		imgThreshold = cv.adaptiveThreshold(imgBlur,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY_INV,15,2)
		imgMedian = cv.medianBlur(imgThreshold,5)

		kernal = np.ones((3,3),np.uint8)
		imgDilate = cv.dilate(imgMedian,kernal, iterations = 1)

		checkParkingSpace(imgDilate)

		t1 = threading.Thread(target=get_input)
		t1.start()


		#cv.imshow('Image',ims)
		#cv.imshow('ImageBlur',imgBlur)
		#cv.imshow('ImageThresh',imgThreshold)
		#cv.imshow('ImageMedian',imgMedian)
		#cv.waitKey(1)

except KeyboardInterrupt:
	GPIO.cleanup()
