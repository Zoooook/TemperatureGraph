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

def smooth(data, newData, times):
    for t in times:
        for i in range(1,9):
            if t in data[i]:
                total = data[i][t]
                m = 1
                tminus = t - datetime.timedelta(minutes=m)
                tplus = t + datetime.timedelta(minutes=m)
                while m <= 10 and \
                      tminus in data[i] and \
                      tplus in data[i] and \
                      abs(data[i][t] - data[i][tminus]) < .2 and \
                      abs(data[i][t] - data[i][tplus]) < .2:
                    total += data[i][tminus] + data[i][tplus]
                    m += 1
                    tminus = t - datetime.timedelta(minutes=m)
                    tplus = t + datetime.timedelta(minutes=m)
                newData[i][t] = round(total / (2*m-1), 3)
    return newData

def buildSheetData(data, times, minDatetime, maxDatetime):
    sheetData = []
    t = minDatetime
    while t <= maxDatetime:
        if t in times:
            row = [t.strftime('%Y-%m-%d %H:%M')]
            for i in range(1,9):
                if t in data[i]:
                    row.append(str(data[i][t]))
                else:
                    row.append('')
            sheetData.append(row)
        t += datetime.timedelta(minutes=1)
    return sheetData

def updateSheet(startRow, data):
    service.spreadsheets().values().update(
        spreadsheetId = '1aVMGkidtztSjkal5Jac5daZT2WNvGbUIjD6Hr2SwaWM',
        valueInputOption = 'USER_ENTERED',
        range = 'Data!B' + str(startRow) + ':J',
        body = {'majorDimension': 'ROWS', 'values': data},
    ).execute()

lastTime = 0
lastDay = 0
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
    currentDatetime = datetime.datetime.strptime(currentTime, '%Y-%m-%d %H:%M')

    if currentDay != lastDay:
        files = sorted(listdir('logs'))

        for f in files[:-30]:
            remove('logs/' + f)

        tempData = [None,{},{},{},{},{},{},{},{}]
        times = set()
        for f in files[-9:]:
            with open('logs/' + f, 'r') as file:
                csvData = reader(file)
                for row in csvData:
                    timeKey =  datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M')
                    times.add(timeKey)
                    for i in range(1,9):
                        try:
                            tempData[i][timeKey] = round(float(row[i]), 2)
                        except ValueError:
                            pass

        smoothData = [None,{},{},{},{},{},{},{},{}]
        smooth(tempData, smoothData, sorted(list(times)))
        minDatetime = currentDatetime.replace(hour=0, minute=0) - datetime.timedelta(days=7)
        sheetData = buildSheetData(smoothData, times, minDatetime, currentDatetime)

        rowNum = len(sheetData) + 1
        sheetData.extend([[''] * 9] * (60*24*8-len(sheetData)))
        updateSheet(2, sheetData)
        lastDay = currentDay

    if currentDatetime in times:
        continue

    row = [currentTime] + temps
    with open('logs/' + currentDay + '.csv', 'a') as file:
        file.write(','.join(row) + '\n')
    times.add(currentDatetime)
    for i in range(1,9):
        try:
            tempData[i][currentDatetime] = round(float(row[i]), 2)
        except ValueError:
            pass

    smooth(tempData, smoothData, sorted(list(times))[-11:])
    minDatetime = currentDatetime - datetime.timedelta(minutes=10)
    sheetData = buildSheetData(smoothData, times, minDatetime, currentDatetime)
    rowNum += 1
    updateSheet(rowNum + 1 - len(sheetData), sheetData)
