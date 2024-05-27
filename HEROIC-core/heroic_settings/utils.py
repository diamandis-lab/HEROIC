import os
import shlex
import subprocess
from subprocess import PIPE, Popen
from zipfile import ZipFile
import pandas as pd


def windows_process_running(pname):
    cmd = 'TASKLIST /FI "imagename eq ' + pname + '" /svc /FO csv'
    p = subprocess.Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, close_fds=False)
    stdout, stderr = p.communicate()
    is_running = stdout.decode('ascii') != 'INFO: No tasks are running which match the specified criteria.\r\n'
    return is_running


def windows_taskkill(pname):
    cmd = 'taskkill /IM "' + pname + '" /F'
    p = subprocess.Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, close_fds=False)
    stdout, stderr = p.communicate()
    print(stdout.decode('ascii'))


def zip_folder(dir_home, dir_parent, dir_target, file_extension='zip'):
    os.chdir(dir_parent)
    file_paths = os.listdir(dir_target)
    with ZipFile(dir_target + '.' + file_extension, 'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(dir_target + '/' + file, compresslevel=5)
    os.chdir(dir_home)


def fix_muse_data(fname):  # fixes Muse data files where the beginning of the recording lacks the 'marker' column
    with open(fname, 'r') as fp:
        Lines = fp.readlines()
    count = 0
    eeg_new = []  # adding rows to list and then convert to pd.DataFrame for efficiency
    for line in Lines:
        line_curr = line.strip()
        count += 1
        chunks = line_curr.split(',')
        if count == 1:  # fix heading row with 'marker' missing (timestamps, TP9, AF7, AF8, TP10)
            if len(chunks) == 6:  # in case the column exists but it was named something else
                chunks[5] = 'marker'
            if len(chunks) == 5:
                chunks.append('marker')
        if count > 1:  # fix rows with data, missing values in the 'marker' column at the begining of the recording
            if len(chunks) == 5:
                chunks.append('0')
        eeg_new.append(chunks)
    eeg_new = pd.DataFrame(eeg_new[1:], columns=eeg_new[0])
    eeg_new.to_csv(fname, index=False)

    # removes malformed rows, possibly due to stream drops and reconnects
    # reopens .csv, drops lines with wrong number of columns, saves clean .csv
    with open(fname, 'r') as fp:
        lines = fp.readlines()
    lines = [x.replace('\n', '') for x in lines]  # removes return character at the end of each line
    lines_clean = [line.split(',') for line in lines if len(line.split(',')) == 6]
    eeg_clean = pd.DataFrame(lines_clean[1:], columns=lines_clean[0])
    if len(lines_clean) < len(lines):
        eeg_clean.to_csv(fname, index=False)


def fix_muse_data_old(fname):  # fixes Muse data files where the beginning of the recording lacks the 'marker' column
    with open(fname, 'r') as fp:
        Lines = fp.readlines()
    count = 0
    eeg_new = []  # adding rows to list and then convert to pd.DataFrame for efficiency
    for line in Lines:
        line_curr = line.strip()
        count += 1
        chunks = line_curr.split(',')
        if count == 1:  # fix heading row with 'marker' missing (timestamps, TP9, AF7, AF8, TP10)
            if len(chunks) == 6:  # in case the column exists but it was named something else
                chunks[5] = 'marker'
            if len(chunks) == 5:
                chunks.append('marker')
        if count > 1:  # fix rows with data, missing values in the 'marker' column at the begining of the recording
            if len(chunks) == 5:
                chunks.append('0')
        eeg_new.append(chunks)
    eeg_new = pd.DataFrame(eeg_new[1:], columns=eeg_new[0])
    eeg_new.to_csv(fname, index=False)


