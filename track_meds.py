#!/usr/bin/env python3

from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import RPi.GPIO as GPIO
from time import sleep
from slack_sdk.webhook import WebhookClient
import json

# Google Config
credential_file = "blood-pressure-stats-3437e823e42b.json"
google_sheets_file = "BP Meds Taken"

# RPi Config
gpio_input_pin = 10

# Logging Config
logfile = "bpstatstracker.log"
slack_config_file = "slack-config.json"

with open(slack_config_file, "r") as f:
    slack_config = json.loads(f.read())
    slack_url = slack_config['logs_url']


def log(msg, log_level = "INFO", post_to_slack = True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logmessage = f"{timestamp} BPStatsTracker {log_level} {msg}\n"
    with open(logfile, "a") as log:
        log.write(logmessage)
    if post_to_slack:
        tell_slack(logmessage)


def tell_slack(msg):
    if slack_url == None:
        log("Slack web hook URL not found!", log_level="ERROR", post_to_slack=False)
        return
    slack_logger = WebhookClient(slack_url)
    response = slack_logger.send(text=msg)
    logmessage = f"Posting log message to Slack. Response code: {response.status_code}. Response body: {response.body}"
    loglevel = "INFO" if response.status_code == 200 else "ERROR"
    log(logmessage, log_level=loglevel, post_to_slack=False)


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
    log(f"Wrote meds taken timestamp to Google Sheet {google_sheets_file}")


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(gpio_input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(gpio_input_pin, GPIO.RISING, callback=record_time, bouncetime=500)

log("Waiting for button presses")
while True:
    sleep(5)

#message = input("Press ENTER to quit")

GPIO.cleanup()
