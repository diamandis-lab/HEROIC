import csv
import pathlib
import json

def extract_markers(folder, channels):
    markers = []
    values = []
    filename = folder+'.csv'
    path_csv = pathlib.Path.cwd()/filename
    f = open(path_csv, "r")
    csv_read = csv.reader(f)
    f1 = open("marker_list_"+filename, "w")
    csv_writer1 = csv.writer(f1)
    f2 = open("marker_value_"+filename, "w")
    csv_writer2 = csv.writer(f2)
    for row in csv_read:
        if row[0] == 'timestamps':
            continue
        elif row[channels+1] != '0.0' and row[channels+1] != '0':

            markers.append(float(row[0]))
            values.append(row[channels+1])
    csv_writer1.writerow(markers)
    csv_writer2.writerow(values)
    return

def offset_data(name, time, channels):
    filename = time+"_default_"+name+"-EEG.csv"
    f = open(filename, mode='r', encoding='utf-8-sig')
    csv_read = csv.reader(f)
    f2 = open("offset_"+name+'.csv', "w")
    csv_write = csv.writer(f2)
    entry = []
    offset = 750*(channels-1)
    next(csv_read)
    time_zero = (next(csv_read))[0]
    f.seek(0)
    for row in csv_read:
        if row[0] == 'timestamps':
            csv_write.writerow(row)
            continue
        for ind in range(channels+2):
            if ind == 0:
                if channels == 14:
                    time = (float(row[ind])-float(time_zero))/1000
                else:
                    time = float(row[ind]) - float(time_zero)
                entry.append(time)
            elif ind == channels+1:
                marker = float(row[channels+1])
                entry.append(marker)
            else:
                wave = float(row[ind]) + float(offset)
                offset -= 750
                entry.append(wave)
        csv_write.writerow(entry)
        entry = []
        offset = 750*(channels-1)
    return

#Final Function that will look through the session_info to find the participant id and time stamp to
#to automatically preprocess all files
def session_name(session_info):
    f = open(session_info, mode='r')
    info = json.load(f)
    if info['params']['eeg_device'] == 'EPOC X':
        channels = 14
    name = info['params']['participant_id']
    time = info['params']['timestamp']
    offset_data(name, time, channels)
    extract_markers("offset_" + name, channels)

    f1 = open("session.csv", "w")
    csv_writer1 = csv.writer(f1)
    csv_writer1.writerow([name, channels])
    return

session_name('session_info.json')

# offset_data("20210617-140433_default_blue_whale-EEG.csv", 14)
#offset_data("20210526-095244_default_uncle-shark - Copy.csv", 4)
#offset_data("file-racoon.csv", 14)


#(extract_markers('20210526-095244_default_uncle-shark - Copy.csv'))