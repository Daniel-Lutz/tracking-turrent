#!/usr/bin/env python3  <- code only works for python3
import pigpio
from time import sleep

# Start the pigpiod daemon
import subprocess

# output of pigpiod command is initalized as None and exit status to 1 indicating the daemon has not started yet
result = None
status = 1

# 3 attempts to open the Daemon
for x in range(3):
    p = subprocess.Popen('sudo pigpiod', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # runs command through shell, captures the sdout and sderr
    result = p.stdout.read().decode('utf-8')  # reads output from process, decodes if from byte to string, and stores in result
    status = p.poll()  # records th exit status of the dameon
    if status == 0:
        break
    sleep(0.2)
    
#debugging if dameon doesn't start
if status != 0:
    print(status, result)
'''
> Use the DMA PWM of the pigpio library to drive the servo
> Map the servo angle (0 ~ 180 degree) to (-90 ~ 90 degree)

'''

# initializing class to interface with servo PWM
class Servo():
    MAX_PW = 2500  # 0.5/20*100
    MIN_PW = 500 # 2.5/20*100
    _freq = 50 # 50 Hz, 20ms
 
    #initialize servo
    def __init__(self, pin, min_angle=-90, max_angle=90):

        self.pi = pigpio.pi()
        self.pin = pin 
        self.pi.set_PWM_frequency(self.pin, self._freq)
        self.pi.set_PWM_range(self.pin, 10000)      
        self.angle = 0
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.pi.set_PWM_dutycycle(self.pin, 0)

    # function to set servo max and min angles to prevent damage
    def set_angle(self, angle):
        if angle > self.max_angle:
            angle = self.max_angle
        elif angle < self.min_angle:
            angle = self.min_angle
        self.angle = angle
        #sets servo angle
        duty = self.map(angle, -90, 90, 250, 1250)
        self.pi.set_PWM_dutycycle(self.pin, duty)

    def get_angle(self):
        return self.angle

    # will be called automatically when the object is deleted
    # def __del__(self):
    #     pass

    #converts the input angle to the corresponding output PWM Duty Cycle for the servos
    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


if __name__ =='__main__':
    from vilib import Vilib
    Vilib.camera_start(vflip=True,hflip=True) 
    Vilib.display(local=True,web=True)

    # Servo Object initialization
    pan = Servo(pin=13, max_angle=90, min_angle=-90)
    tilt = Servo(pin=12, max_angle=90, min_angle=-90)
    shoot = Servo(pin=19, max_angle=90, min_angle=-90)
    panAngle = 0
    tiltAngle = 0
    shootAngle = 0
    pan.set_angle(panAngle)
    tilt.set_angle(tiltAngle)
    shoot.set_angle(shootAngle) # servo on trigger to shoot
    sleep(1)

    # Main loop
    while True:
        for angle in range(0, 90, 1):
            pan.set_angle(angle)
            tilt.set_angle(angle)
            shoot.set_angle(angle)
            sleep(.01)
        sleep(.5)
        for angle in range(90, -90, -1):
            pan.set_angle(angle)
            tilt.set_angle(angle)
            shoot.set_angle(angle)
            sleep(.01)
        sleep(.5)
        for angle in range(-90, 0, 1):
            pan.set_angle(angle)
            tilt.set_angle(angle)
            shoot.set_angle(angle)
            sleep(.01)
        sleep(.5)
