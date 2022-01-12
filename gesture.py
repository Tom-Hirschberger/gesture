#!/usr/bin/env python3
from apds9960.const import *
from apds9960 import APDS9960
import RPi.GPIO as GPIO
import smbus
import sys
import signal
from time import sleep
import requests
import gesture_config as cfg
import pprint


def exit_handler(signal, frame):
    global running
    global apds
    running = False
    if apds:
        apds.disableGestureSensor()
    print()
    sys.exit(0)
    
# Attach a signal handler to catch SIGINT (Ctrl+C) and exit gracefully
signal.signal(signal.SIGINT, exit_handler)

port = 1
bus = smbus.SMBus(port)

apds = APDS9960(bus)

ir_flag = False
def intH(channel):
    global ir_flag
    ir_flag = True

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN)

dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
}

try:
    # Interrupt-Event hinzufuegen, steigende Flanke
    GPIO.add_event_detect(7, GPIO.FALLING, callback = intH)

    print("Gesture Test")
    print("============")
    apds.enableGestureSensor()
    apds.setGestureLEDDrive(APDS9960_LED_DRIVE_100MA)
    apds.setGestureGain(APDS9960_GGAIN_4X)
    
    running = True

    while running:
        if ir_flag:
            GPIO.remove_event_detect(7)
            ir_flag = False
            if apds.isGestureAvailable():
                motion = apds.readGesture()
                gesture = dirs.get(motion, "unknown")
                print("Gesture={}".format(gesture))
                cur_event = cfg.gesture_events.get("default", None)
                cur_event = cfg.gesture_events.get(gesture, cur_event)
                
                if not cur_event is None:
                    pprint.pprint(cur_event, indent=4)
                    if not cur_event.get("url", None) is None:
                        if cur_event.get("type", "GET") is "GET":
                            try:
                                r = requests.get(cur_event["url"], headers=cur_event.get("headers", None))
                            except:
                                pass
                        elif cur_event.get("type", None) is "POST":
                            try:
                                r = requests.post(cur_event["url"], json=cur_event.get("data", None), headers=cur_event.get("headers", None))
                            except:
                                pass
                        else:
                            print("Unknown type %s" %cur_event.get("type", None))
            GPIO.add_event_detect(7, GPIO.FALLING, callback = intH)
        sleep(cfg.time_between_check)


finally:
    GPIO.cleanup()
    print("Bye")
