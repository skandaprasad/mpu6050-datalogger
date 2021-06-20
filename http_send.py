#!/usr/bin/env python3
import serial
import argparse
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("port", help="Serial port to watch")
parser.add_argument("-b", "--bufsize", type=int, default=16, help="Size of row buffer")
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
args = parser.parse_args()
bufsize = args.bufsize
verbose = args.verbose
port = args.port

# Setup credentials
# Use the sheet ID of the Google sheet you want to update
SPREADSHEET_ID = '14pMW3vpIZEMXM9uXINPPR0OhEUq64A7xCkvVNCQ9wAo'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Use the credentials file that you got when you make your GCP service service account
# Set the environment variable SERVICE_ACCOUNT_FILE to point to your credentials JSON file
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

serialPort = serial.Serial(port, baudrate=9600)
serialPort.flushInput()
count = 0
ok_count = 0

# Wait until a "start" is received on the serial port
start = ""
while(start != "start"):
    ser_bytes = serialPort.readline()
    start = ser_bytes[0:len(ser_bytes) - 2].decode('utf-8').strip()

corner_top_left_row = 2
while(True):
    try:
        curr_range = "A" + str(corner_top_left_row) + ":H" + str(corner_top_left_row + bufsize - 1)
        buffer = []

        # Buffer fixed sets of rows, and send one buffer at a time to stay within GCP rate limit
        for i in range(0, bufsize):
            val = []
            val.extend(datetime.now().strftime("%d-%m-%Y,%H:%M:%S").split(','))
            ser_bytes = serialPort.readline()
            val.extend(ser_bytes[0:len(ser_bytes) - 2].decode('utf-8').strip().split(','))
            buffer.append(val)

        #  Send buffer once it is full, by calling the Sheets API
        #  Ref: https://developers.google.com/sheets/api/reference/rest
        batch_update_values_request_body = {
            'value_input_option': 'RAW',
            'data': [
                {
                    "majorDimension": "ROWS",
                    "range": curr_range,
                    "values": buffer
                }
            ]
        }

        request = service.spreadsheets().values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=batch_update_values_request_body
                )
        response = request.execute()

        count += 1
        corner_top_left_row += bufsize

        if(verbose):
            print("Response {}".format(count))
            pprint(response)
            print("")
    except KeyboardInterrupt:
        print("")
        print("Summary:")
        print("Total requests: {}".format(count))
        break
    except Exception as e:
        print(e)
        break
