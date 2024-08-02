This script pulls temperature data from a WS-3000 weather station attached to a Raspberry Pi, and pushes it to a [spreadsheet](https://docs.google.com/spreadsheets/d/1aVMGkidtztSjkal5Jac5daZT2WNvGbUIjD6Hr2SwaWM/edit?gid=1714012920).

    sudo apt-get install build-essential git libusb-dev libudev-dev nodejs npm
    npm install EpicVoyage/ambientweather-ws3000
    pip install google-api-python-client Naked

https://developers.google.com/sheets/api/quickstart/python
