import os
import urllib.request
import sys
import time
import logging
import requests
from tqdm import tqdm
import schedule
from datetime import datetime
import threading
import keyboard


def is_valid_date(date_str):
    if len(date_str) != 8:
        return False

    try:
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])

        if not (1 <= month <= 12):
            return False

        datetime(year, month, day)

        # current_year = datetime.now().year
        # if year > current_year:
        #     return False

        return True

    except ValueError:
        return False


def check_files(date, config):
    file_types = [f'TC_{date}.txt', 'TickData_structure.dat', 'TC_structure.dat', f'WEBPXTICK_DT-{date}.zip']
    data_dir = config.get('downloader', 'data_dir')
    all_files_exist = True
    for file_type in file_types:
        filepath = os.path.join(data_dir, date, file_type)
        if not os.path.isfile(filepath):
            all_files_exist = False
            break

    return all_files_exist


def index2date(index, config):
    try:
        index = int(index)
        url = f'https://links.sgx.com/1.0.0/derivatives-historical/{index}/TC.txt'

        request = urllib.request.urlopen(url, timeout=config.getint('network', 'timeout'))
        filename = str(request.headers.get('Content-Disposition', ''))

        if (index >= 2755 or 31 <= index <= 903) and '_' in filename:
            date = filename.split('_')[1].split('.')[0]
        elif (903 < index < 2755 or 0 < index <= 30) and '=' in filename:
            date = filename.split('=')[1][:8]
        else:
            date = '0'

    except Exception as e:
        logging.warning('Index {} is failure, {}'.format(str(index), str(e)))
        date = 'INVALID'

    return date


def update_index(config):
    with open(config.get('history', 'latest_index_file'), 'r') as f:
        date_index = f.read()

    if date_index:
        latest_date, latest_index = date_index.split()
        latest_index = int(latest_index)
    else:
        latest_date, latest_index = config.get('index', 'latest_date'), config.getint('index', 'latest_index')

    while True:
        date = index2date(latest_index+1, config)  # check if the website have new file for new date
        if date == '0':
            break
        else:
            latest_date = date
            latest_index += 1
            add_to_dict(date, latest_index, config)

    with open(config.get('history', 'latest_index_file'), 'w') as f:
        f.write(latest_date + ' ' + str(latest_index))


def add_to_dict(date, index, config):
    with open(config.get('history', 'date_index_dict_file'), 'r') as f:
        content = f.read()
        if content:
            date_index_dict = eval(content)
        else:
            date_index_dict = {}

    date_index_dict[date] = index
    with open(config.get('history', 'date_index_dict_file'), 'w') as f:
        f.write(str(date_index_dict))


def create_dict(config):
    update_index(config)
    start_index = config.getint('dictionary', 'start_index')
    with open(config.get('history', 'latest_index_file'), 'r') as f:
        date_index = f.read().split(' ')
    last_index = int(date_index[1])  # this is the latest date in the web

    if os.path.exists(config.get('history', 'date_index_dict_file')):
        with open(config.get('history', 'date_index_dict_file')) as f:
            data = f.read()
            date_index_dict = eval(data)
    else:
        date_index_dict = {}
    for i in range(start_index, last_index + 1):
        date_index_dict[index2date(i, config)] = i
    with open(config.get('history', 'date_index_dict_file'), 'w') as f:
        f.write(str(date_index_dict))

    logging.info(f'Create date_index dictionary from index {start_index} to {last_index}')


def download_report(bytes_so_far, total_size, filename, start_time=None):
    percent = (bytes_so_far / total_size) * 100
    progress_message = f"{filename} Downloaded {bytes_so_far} of {total_size} bytes ({percent:.2f}%)"

    if start_time:
        elapsed_time = time.time() - start_time
        speed = bytes_so_far / elapsed_time if elapsed_time > 0 else 0
        remaining_time = (total_size - bytes_so_far) / speed if speed > 0 else float('inf')
        progress_message += f" - {remaining_time:.2f} seconds remaining"

    sys.stdout.write(f"\r{progress_message}")
    sys.stdout.flush()

    if bytes_so_far >= total_size:
        sys.stdout.write("\n")


def downloader(date, index, config):

    file_types = ['TC.txt', 'TickData_structure.dat', 'TC_structure.dat', 'WEBPXTICK_DT.zip']

    data_dir = os.path.join(str(config.get('downloader', 'data_dir')), date)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    download_success = True
    for datatype in file_types:
        try:
            url = f'https://links.sgx.com/1.0.0/derivatives-historical/{index}/{datatype}'
            response = requests.get(url, stream=True)

            if response.status_code != 200:
                logging.warning(f"Failed to download {datatype} for {date}. HTTP Status Code: {response.status_code}")
                download_success = False
                continue

            total_size = int(response.headers.get('content-length', 0))
            chunk_size = config.getint('downloader', 'chunk_size')

            if datatype == 'WEBPXTICK_DT.zip':
                filename = f'WEBPXTICK_DT-{date}.zip'
            elif datatype == 'TC.txt':
                filename = f'TC_{date}.txt'
            else:
                filename = datatype

            filepath = os.path.join(data_dir, filename)

            start_time = time.time()  # start the time to download

            with open(filepath, "wb") as file, tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        bytes_so_far = file.tell()
                        pbar.update(len(chunk))
                        download_report(bytes_so_far, total_size, filename, start_time)
            print("✔️ Files downloaded!")

        except Exception as e:
            logging.error(f'{date} download failed: {str(e)}')
            download_success = False
            with open(config.get('history', 'missing_index_file'), 'a') as f:
                f.write(f'{index} ')

    return download_success


def download_newest_file(config):
    update_index(config)
    with open(config.get('history', 'latest_index_file'), 'r') as f:
        date_index = f.read()
    date, index = date_index.split()
    downloader(date, index, config)
    logging.info(f'Downloading the latest file with date: {date} and URL index: {index}')


def download_history(date, config):
    check = check_files(date, config)
    if check:
        logging.info(f"All data for {date} have already been downloaded.")

    else:
        try:
            update_index(config)
            with open(config.get('history', 'date_index_dict_file'), 'r') as f:
                data = f.read()
            if data:
                date_index_dict = eval(data)
            else:
                date_index_dict={}
                
            index = date_index_dict[str(date)]
            downloader(date, index, config)

            logging.info(f'Downloading history for date: {date} ...')
            return
        except Exception as e:
            logging.error(f'{date} is not in date_index_dict, please check: {str(e)}')


stop_flag = threading.Event()


def display_waiting_progress():
    print('The program in automation download mode !!!')
    logging.info("Automation program started.")
    progress_symbols = ["|", "/", "-", "\\"]
    while not stop_flag.is_set():
        for symbol in progress_symbols:
            if stop_flag.is_set():
                break
            sys.stdout.write(f"\r⌛ wait to 7:00 am... {symbol}")
            sys.stdout.flush()
            time.sleep(0.5)
    print("\nAutomation stopped.")


def re_download(config):
    missing_index_file = config.get('history', 'missing_index_file')

    with open(missing_index_file, 'r') as f: 
        index_list = f.read().split()

    if len(index_list) > 0:
        for i in index_list:
            date = index2date(int(i), config)

            if date != '0' and date != 'INVALID':
                success = downloader(date, int(i), config)

                if success:
                    logging.info(f"Re-downloading the files for date {date} with index url {i} successfully! ")
                    index_list = [x for x in index_list if x != i]  # remove the index from the missing file
                else:
                    logging.error(f"Re-downloading the files for date {date} with index url {i} failed! ")

        with open(missing_index_file, 'w') as f:
            for index in index_list:
                f.write(f"{index} ")


def run_scheduled_task(config):
    schedule.every().day.at(config.get('automation', 'schedule_check_time')).do(download_newest_file, config)
    schedule.every().day.at(config.get('automation', 'schedule_re_download_time')).do(re_download, config)
    while not stop_flag.is_set():
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(str(e) + ' - Automation failed!')
            break


def wait_for_exit_key():
    print("Press 'q' to stop the automation mode...")
    while True:
        if keyboard.is_pressed('q'):
            stop_flag.set()
            logging.info("Automation program ended.")
            break
        time.sleep(0.1)


def start_automation(config):
    progress_thread = threading.Thread(target=display_waiting_progress)
    progress_thread.daemon = True
    progress_thread.start()

    exit_thread = threading.Thread(target=wait_for_exit_key)
    exit_thread.daemon = True
    exit_thread.start()

    run_scheduled_task(config)

