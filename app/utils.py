from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import *
import re


def convert_in_hours(time):
    per_hour = 60
    difference = time - per_hour
    if difference >= 0:
        hour = 0
        while per_hour <= time:
            calc = time - per_hour
            time = calc
            hour += 1
            if calc == 0:
                calc = "00"
        duration =str(hour)+":"+str(calc)
    else:
        duration = "00:"+str(time)
    return duration

def convert_in_minutes(time):
    time_split = time.split(":")
    var_hour = int(time_split[0])
    var_minute = int(time_split[1])
    var_seconds = int(time_split[2])
    fix_minutes = 0
    if var_hour!= 0:
        minutes = 60
        for i in range(1, var_hour):
            minutes +=60
        fix_minutes = var_minute+minutes

    duration_in_minutes = var_minute+fix_minutes
    if var_seconds != 0 :
        duration_str = str(duration_in_minutes)
        seconds_str = str(var_seconds)
        total_duration = duration_str+"."+seconds_str
        duration_in_minutes = float(total_duration)
    return duration_in_minutes

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

def duration_format_allowed(par):
    print(par)
    print(type(par))
    # [a-zA-Z0-9()$%_/.]*$
    allowed_characters = ['1','2','3','4','5','6','7','8','9','0','.']
    if any(x not in allowed_characters for x in par):
        print("error: invalid character")
        return False
    else:
        print("no error")
        return True