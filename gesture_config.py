#!/usr/bin/env python3
time_between_check = 0.2
gesture_events = {
    "default": {
        "type": "GET",
        "url": "http://10.18.8.31:8080/api/userpresence/true"
    },
    "right": {
        "type": "POST",
        "url": "http://10.18.8.31:8080/api/notification/SCREEN_ON",
        "data": {'forced':True}
    },
    "left": {
        "type": "POST",
        "url": "http://10.18.8.31:8080/api/notification/SCREEN_OFF",
        "data": {'forced':True}
    },
}