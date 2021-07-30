#!/usr/bin/env python3

from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from slack_sdk.webhook import WebhookClient
from gpiozero import Button
from signal import pause
import json

# Google Config
credential_file = "blood-pressure-stats-3437e823e42b.json"
google_sheets_file = "BP Meds Taken"

# RPi Config
gpio_input_pin = 10

# Logging Config
logfile = "bpstatstracker.log"
slack_config_file = "slack-config.json"


def log(msg, log_level = "INFO", post_to_slack = True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logmessage = f"{timestamp} BPStatsTracker {log_level} {msg}\n"
    with open(logfile, "a") as log:
        log.write(logmessage)
    if post_to_slack:
        tell_slack(logmessage)


def tell_slack(msg):
    with open(slack_config_file, "r") as f:
        slack_url = json.loads(f.read()).get('logs_url')
    if not slack_url:
        log("Slack web hook URL not found!", log_level="ERROR", post_to_slack=False)
        return
    slack_logger = WebhookClient(slack_url)
    response = slack_logger.send(text=msg)
    logmessage = f"Posting log message to Slack. Response code: {response.status_code}. Response body: {response.body}"
    loglevel = "INFO" if response.status_code == 200 else "ERROR"
    log(logmessage, log_level=loglevel, post_to_slack=False)


def write_to_spreadsheet():
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


def pressed():
    write_to_spreadsheet()


button = Button(15, pull_up=False)
button.when_pressed = pressed

log("Waiting to record events")
pause()
