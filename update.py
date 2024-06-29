from pickle import load
from googleapiclient.discovery import build
from os.path import exists
from os import mkdir, listdir, remove
import datetime
from time import sleep
from Naked.toolshed.shell import execute_js
from csv import reader

with open('token.pickle', 'rb') as token:
    creds = load(token)
service = build('sheets', 'v4', credentials=creds)
if not exists('logs/'):
    mkdir('logs/')

lastTime = 0
lastDay = 0
rowNum = 0
while True:
    currentTime = str(datetime.datetime.now())[:16]
    if currentTime == lastTime:
        sleep(15)
        continue
    lastTime = currentTime

    execute_js('parse.js')
    with open('temps.csv', 'r') as file:
        csvData = reader(file)
        for row in csvData:
            temps = ['' if x == '' else str(round(float(x)*1.8+32, 2)) for x in row]
            break

    currentDay = currentTime[:10]
    with open('logs/' + currentDay + '.csv', 'a') as file:
        file.write(','.join([currentTime] + temps) + '\n')

    if currentDay != lastDay:
        files = sorted(listdir('logs'))
        for f in files[:-30]:
            remove('logs/' + f)

        sheetData = []
        for f in files[-8:]:
            with open('logs/' + f, 'r') as file:
                csvData = reader(file)
                for row in csvData:
                    sheetData.append(row)
        rowNum = len(sheetData) + 1
        sheetData.extend([[''] * 9] * (60*24*8-len(sheetData)))

        service.spreadsheets().values().update(
            spreadsheetId = '1aVMGkidtztSjkal5Jac5daZT2WNvGbUIjD6Hr2SwaWM',
            valueInputOption = 'USER_ENTERED',
            range = 'Data!B2:J',
            body = {'majorDimension': 'ROWS', 'values': sheetData},
        ).execute()

        lastDay = currentDay

    sheetData = [[currentTime] + temps]
    rowNum += 1

    service.spreadsheets().values().update(
        spreadsheetId = '1aVMGkidtztSjkal5Jac5daZT2WNvGbUIjD6Hr2SwaWM',
        valueInputOption = 'USER_ENTERED',
        range = 'Data!B' + str(rowNum) + ':J',
        body = {'majorDimension': 'ROWS', 'values': sheetData},
    ).execute()
