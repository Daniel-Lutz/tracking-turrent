import cv2
from picamera2 import Picamera2
import time
import numpy as np
import RPi.GPIO as GPIO
from servo import Servo

#naming camera
picam2 = Picamera2()

#initializing servo pan and tilt angle (0-180); initializing shoot function (0,1)
pan=Servo(pin=13)
tilt=Servo(pin=12)
shoot=Servo(pin=19)

panAngle=0
tiltAngle=0
shootAngle=0

pan.set_angle(panAngle)
tilt.set_angle(tiltAngle)
shoot.set_angle(shootAngle)

#Turning on camera, initalizing display settings (600,400 max performance with smallest functional window)
dispW=600
dispH=400
picam2.preview_configuration.main.size = (dispW,dispH)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate=30
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
fps=0
pos=(30,60)
font=cv2.FONT_HERSHEY_SIMPLEX
height=1.5
weight=3
myColor=(0,0,255)

#initializing control window (use mouse or arrow keys to interact with window)
track=0
def onTrack7(val):
    global track
    track=val

cv2.namedWindow('Track')

cv2.createTrackbar('Train-0 Track-1','Track',0,1,onTrack7)

#Face track algorithm from haar cascade library
faceCascade=cv2.CascadeClassifier('./haar/haarcascade_frontalface_default.xml')

#starting camera, face detection, and initializing white fire spread box and cross hair
while True:
    tStart=time.time()
    frame= picam2.capture_array()
    cv2.putText(frame,str(int(fps))+' FPS',pos,font,height,myColor,weight)
    frameGray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces=faceCascade.detectMultiScale(frameGray,1.3,5)
    cv2.rectangle(frame,(int(dispW/2-dispW/8),int(dispH/2-dispW/8)),(int(dispW/2+dispW/8),int(dispH/2+dispW/8)),(255,255,255),2)
    cv2.line(frame,(int(dispW/2+10),int(dispH/2)),(int(dispW/2-10),int(dispH/2)),(255,255,255),1)
    cv2.line(frame,(int(dispW/2),int(dispH/2+10)),(int(dispW/2),int(dispH/2-10)),(255,255,255),1)
    
#When face is detected
    for face in faces:
#coordinates of box around target (upper leftx, upper lefty), (lower rightx, lower righty)
        x,y,w,h=face
        smulx=int(x+w/4)
        smuly=int(y+h/4)
        smlrx=int(x+3*w/4)
        smlry=int(y+3*h/4)

#        cv2.rectangle(frame,(smulx,smuly),(smlrx,smlry),(255,255,255),2)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,255),2)
        
#Allignes target to center of screen; only starts when track is on
        if track==1:
#calculates difference between center of screen and center of box around target
            errorpan=(x+w/2)-dispW/2
            errortilt=(y+h/2)-dispH/2
            
#Slows turning speed as target approaches center of screen to prevent overturining from momentum
            panAngle-=errorpan/30
            pan.set_angle(panAngle)
            tiltAngle-=errortilt/30
            tilt.set_angle(tiltAngle)

#Places box around target when detected, (white box = out of range, yellow = approaching range, red box = within range and shooting)
            if int(dispW/2+dispW/8)>x and int(dispW/2-dispW/8<x+w) and int(dispH/2+dispW/8)>y and int(dispH/2-dispW/8<y+h):
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),3)
                
            if dispW/2>x and dispW/2<x+w and dispH/2>y and dispH/2<y+h:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),3)
                
            if dispW/2>smulx and dispW/2<smlrx and dispH/2>smuly and dispH/2<smlry:
                #cv2.rectangle(frame,(smulx,smuly),(smlrx,smlry),(0,0,255),2)
                shoot.set_angle(30)
                time.sleep(0.1)
                shoot.set_angle(0)
                
#Camera window; stops cv2 when q is pressed; 
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1)==ord('q'):
        break
#fps calculation
    tEnd=time.time()
    loopTime=tEnd-tStart
    fps=.9*fps + .1*(1/loopTime)
cv2.destroyAllWindows()
