from filelock import FileLock
from pathlib import Path
import pandas as pd
import os

FUT1 = 'ZB'
FUT2 = 'ZN'
RUN = '1'

WORK_DIR = Path().resolve()
HIST_DATA_PATH = '/Users/rednerka/Desktop/USBonds/USBond-main/hist_data/'
LIVE_DATA_PATH = f'/Users/rednerka/Desktop/USBonds/USBond-main/live_data/run{RUN}/'
LOCK_PATH = '/Users/rednerka/Desktop/USBonds/USBond-main/'

def getData():
    pass

def push_commit():
    os.system('git add .')
    os.system("git commit -m 'update data'")
    os.system("git push origin main")

def main():
    while True:
        getData()
        push_commit()

if __name__ == '__main__':
    main()