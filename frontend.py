from oauth2client.service_account import ServiceAccountCredentials
import gspread
import time
import os
import numpy as np
import streamlit as st


SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

class GetData:
    def __init__(self):
        self.scope =['https://www.googleapis.com/auth/spreadsheets',
                     'https://www.googleapis.com/auth/drive.file',
                     'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
                SERVICE_ACCOUNT_FILE,
                self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open("MPU6050_Log").sheet1
        self.chart = st.line_chart(np.array([[5.0]]))

    def gettime_insecs(self, st, en):
        self.start_hr = st[3]
        self.start_min = st[4]
        self.start_sec = st[5]
        self.end_hr = en[3]
        self.end_min = en[4]
        self.end_sec = en[5]
        startSumSec = (self.start_hr * 3600) + (self.start_min * 60) + self.start_sec
        endSumSec = (self.end_hr * 3600) + (self.end_min * 60) + self.end_sec
        return endSumSec - startSumSec

    def good_posturetime(self, val, cursor, thresh=-15):
        started = time.localtime(time.time())
        st.success("Good Posture")
        while val >= thresh:
            val = self.sheet.cell(cursor, 7).value
            val = float(val)
            self.chart.add_rows(np.array([[val]]))
            cursor += 2
            print(cursor)
            time.sleep(1)
        ended = time.localtime(time.time())
        return self.gettime_insecs(started, ended), cursor

    def bad_posturetime(self, val, cursor, thresh=15):
        started = time.localtime(time.time())
        st.error("Bad Posture")
        while val <= thresh:
            val = self.sheet.cell(cursor, 7).value
            val = float(val)
            self.chart.add_rows(np.array([[val]]))
            cursor += 2
            time.sleep(1)
            print(cursor)
        ended = time.localtime(time.time())
        return self.gettime_insecs(started, ended), cursor



    def start_read(self, startingPoint=2, required_col=7 ):
        cursor = startingPoint
        while True:
            try:
                val = self.sheet.cell(cursor, required_col).value
                val = float(val)
                print(val)
                if val > 15:
                    gtime, cursor = self.good_posturetime(val=val,cursor=cursor)
                    print(val)
                    st.write("Good Posture time in seconds:", gtime)
                    print(f'goodPosture:{gtime}')
                elif val < -15:
                    btime, cursor= self.bad_posturetime(val=val, cursor=cursor)
                    st.write("Bad Posture time in seconds:", btime)
                    print(val)
                    print(f'BadPosture:{btime}')
                else:
                    cursor += 1
                    self.chart.add_rows(np.array([[float(val)]]))



            except:
                    pass

st.title("Posture Detection")
g = GetData()
getdata = st.checkbox("Get Data")

if getdata:
    g.start_read(startingPoint=2913)

