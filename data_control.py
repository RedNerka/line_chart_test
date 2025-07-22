from filelock import FileLock
from pathlib import Path
import os
import time
from datetime import datetime, timedelta, time as dtime
import pytz
import shutil
import pandas as pd
import numpy as np

FUT1 = 'ZB'
FUT2 = 'ZN'
RUN = '1'

WORK_DIR = Path().resolve()
HIST_DATA_SRC_PATH = '/Users/rednerka/Desktop/USBonds/USBond-main/hist_data/'
LIVE_DATA_SRC_PATH = f'/Users/rednerka/Desktop/USBonds/USBond-main/live_data/run{RUN}/'
LOCK_PATH = '/Users/rednerka/Desktop/USBonds/USBond-main/'

HIST_DATA_PATH = f'{WORK_DIR}/data/'
LIVE_DATA_PATH = f'{WORK_DIR}/live_data/'
PLOT_PATH = f'{WORK_DIR}/plot_data/'

tz = pytz.timezone("US/Central")

rth_start = dtime(8, 30)
rth_end = dtime(15, 0)

def getData(future):
    filename = f'{future}_live_data_MIDPOINT.csv'
    path = LIVE_DATA_SRC_PATH + filename
    shutil.copy(path, LIVE_DATA_PATH + filename)

def move_data(dt):
    all_files = [file for file in os.listdir(LIVE_DATA_PATH) if file.endswith('.csv')]
    if len(all_files) <= 0:
        return
    for file in all_files:
        shutil.rmtree(file)
    dt = dt.date().strftime('%Y%m%d')
    shutil.copy(HIST_DATA_SRC_PATH + dt + '_' + file, HIST_DATA_PATH + dt + '_' + file)

def checkRTH(is_rth): #checked
    curr_time = time.time()
    local_dt = datetime.fromtimestamp(curr_time, tz=tz)
    if rth_start <= local_dt.time() <= rth_end:
        is_rth = True
    elif local_dt.time() > rth_end and is_rth:
        is_rth = False
        move_data(local_dt)
    else:
        pass
    return is_rth, local_dt.time()

def push_commit():
    os.system('git add .')
    os.system("git commit -m 'update data'")
    os.system("git push origin main")

def data_process(start):
    dates = []
    for i in range(30, -1, -1):
        curr = (pd.to_datetime(start).date() - pd.Timedelta(days=i)).strftime('%Y%m%d')
        dates.append(curr)

    diff = {}
    for curr in dates:
        try:
            curr_prod1 = pd.read_csv(HIST_DATA_PATH + f'{curr}_{FUT1}_live_data_MIDPOINT.csv', header=None)
            curr_prod2 = pd.read_csv(HIST_DATA_PATH + f'{curr}_{FUT2}_live_data_MIDPOINT.csv', header=None)
            curr_diff = ((curr_prod1[10] - curr_prod2[10]) * 10000).to_numpy()
            timestr = pd.to_datetime(curr_prod1[2], unit='s', utc=True).dt.tz_convert("US/Central").dt.strftime("%Y-%m-%d %H:%M:%S US/Central").tolist()
            
        except Exception as e:
            continue
        hist_i = 1
        hist_count = 0
        temp = []
        while hist_count < 14:
            hist_curr = (pd.to_datetime(curr).date() - pd.Timedelta(days=hist_i)).strftime('%Y%m%d')
            # print(hist_curr)
            try:
                curr_hist_data_prod1 = pd.read_csv(HIST_DATA_PATH + f'{hist_curr}_{FUT1}_live_data_MIDPOINT.csv', header=None)
                curr_hist_data_prod2 = pd.read_csv(HIST_DATA_PATH + f'{hist_curr}_{FUT2}_live_data_MIDPOINT.csv', header=None)
                temp += ((curr_hist_data_prod1[10] - curr_hist_data_prod2[10]) * 10000).tolist()
                hist_count += 1
            except Exception as e:
                pass
            hist_i += 1
        
        temp = np.array(temp)
        mean_ytm = temp.mean()
        std_ytm = temp.std()

        curr_diff_norm = (curr_diff - mean_ytm) / std_ytm
        diff[curr] = (curr_diff.tolist(), curr_diff_norm.tolist(), timestr)

    plot_data = []
    plot_data_norm = []
    plot_dates = []
    for _, vals in diff.items():
        plot_data.extend(vals[0])
        plot_data_norm.extend(vals[1])
        plot_dates.extend(vals[2])  # 每个val都用相同的date打上标签

    idx = range(0, len(plot_data))
        
    res = pd.DataFrame({
        'idx': idx,
        'ytm_diff': plot_data,
        'ytm_diff_norm': plot_data_norm,
        'time': plot_dates
    })
    res.to_csv(PLOT_PATH + 'plot_data.csv', index=False, header=True)
    return len(res)

def getMeanStd(start):
    hist_i = 1
    hist_count = 0
    temp = []
    while hist_count < 14:
        hist_curr = (pd.to_datetime(start).date() - pd.Timedelta(days=hist_i)).strftime('%Y%m%d')
        # print(hist_curr)
        try:
            curr_hist_data_prod1 = pd.read_csv(HIST_DATA_PATH + f'{hist_curr}_{FUT1}_live_data_MIDPOINT.csv', header=None)
            curr_hist_data_prod2 = pd.read_csv(HIST_DATA_PATH + f'{hist_curr}_{FUT2}_live_data_MIDPOINT.csv', header=None)
            temp += ((curr_hist_data_prod1[10] - curr_hist_data_prod2[10]) * 10000).tolist()
            hist_count += 1
        except Exception as e:
            pass
        hist_i += 1
    
    temp = np.array(temp)
    mean_ytm = temp.mean()
    std_ytm = temp.std()
    return (float(mean_ytm), float(std_ytm))

def live_data_process(read_index, write_index, mean, std):
    prod1 = pd.read_csv(LIVE_DATA_PATH + f'{FUT1}_live_data_MIDPOINT.csv', header=None).iloc[read_index:]
    prod2 = pd.read_csv(LIVE_DATA_PATH + f'{FUT2}_live_data_MIDPOINT.csv', header=None).iloc[read_index:]
    if len(prod1) < len(prod2):
        length = len(prod1)
        prod2 = prod2.iloc[:length]
    elif len(prod1) > len(prod2):
        length = len(prod2)
        prod1 = prod1.iloc[:length]
    else:
        length = len(prod1)
    read_index += length

    diff = ((prod1[10] - prod2[10]) * 10000).to_numpy()
    diff_norm = (diff - mean) / std
    timestr = pd.to_datetime(prod1[2], unit='s', utc=True).dt.tz_convert("US/Central").dt.strftime("%Y-%m-%d %H:%M:%S US/Central").tolist()
    idx = range(write_index, write_index + length)
    write_index += length
    new_data = pd.DataFrame({
        'idx': idx,
        'ytm_diff': diff.tolist(),
        'ytm_diff_norm': diff_norm.tolist(),
        'time': timestr
    })

    new_data.to_csv(PLOT_PATH + 'plot_data.csv', mode='a', index=False, header=False)
    return (read_index, write_index)

def main():
    is_rth = False
    today_time = time.time()
    start = datetime.fromtimestamp(today_time, tz=tz).strftime('%Y%m%d')

    mean_val, std_val = getMeanStd(start)

    read_idx = 0
    write_idx = data_process(start)
    print('hist data processing...done')
    push_commit()
    print('data update push...done')

    while True:
        is_rth, curr_time = checkRTH(is_rth)

        if is_rth:
            print('in rth, getting data...')
            with FileLock(LOCK_PATH + f'{FUT1}.lock'):
                getData(FUT1)
            with FileLock(LOCK_PATH + f'{FUT2}.lock'):
                getData(FUT2)
            print('live data processing...')
            read_idx, write_idx = live_data_process(read_idx, write_idx, mean_val, std_val)
            print('new data update push...')
            push_commit()
            print('sleep 10')
            time.sleep(10)
        elif not is_rth and curr_time > rth_end:
            push_commit()
            print('job done, exiting...')
            break
        else:
            print('not in rth...sleep 60')
            time.sleep(60)
            

if __name__ == '__main__':
    main()