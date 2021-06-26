#!/usr/bin/env python3

from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import RPi.GPIO as GPIO
from time import sleep


credential_file = "blood-pressure-stats-3437e823e42b.json"
google_sheets_file = "BP Meds Taken"
gpio_input_pin = 10
logfile = "bpstatstracker.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logmessage = "%s %s\n" % (timestamp, msg)
    with open(logfile, "a") as log:
        log.write(logmessage)


def button_pressed(channel):
    log("button pressed")


def record_time(channel):
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credential_file, scopes)
    meds_file = gspread.authorize(credentials)
    sheet = meds_file.open(google_sheets_file)
    sheet = sheet.sheet1

    today = date.today().strftime("%m/%d/%Y")
    now = datetime.now().strftime("%H:%M:%S")

    sheet.append_row([today, now])
    log("Wrote timestamp to Google Sheet '%s'" % (google_sheets_file))


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(gpio_input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(gpio_input_pin, GPIO.RISING, callback=record_time, bouncetime=200)

log("Waiting for button presses")
while True:
    sleep(5)

#message = input("Press ENTER to quit")

GPIO.cleanup()
