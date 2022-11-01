import csv
import json
import pathlib

#requires session1, session3, session_info and csv file of session2 to create a new csv file called speech.csv with all the information

def colors_time(words, please_time_conc, please_time_dis, session_start_conc, session_start_dis, cols_abs):
    # starts at four because that's when the first colour appears
    for word in range(4, len(words)):
        col_name = words[word]['word']
        col_time = words[word]['start_time']
        if word in range(4, 14):
            abs_time = round(col_time - please_time_conc, 2) + session_start_conc
            cols_abs.append((col_name, abs_time))
        elif word in range(18, len(words)):
            abs_time = round(col_time - please_time_dis, 2) + session_start_dis
            cols_abs.append((col_name, abs_time))
        else:  # range (14, 18) is the second please speak your answer
            continue
    return cols_abs


def calc_absolute_time(session1, session3, sessioninfo):
    path1 = pathlib.Path(session1)
    #path1 = pathlib.Path.cwd().parent/'sibley_38'/'output'
    path3 = pathlib.Path(session3)
    pathinfo = pathlib.Path(sessioninfo)
    #pathinfo = pathlib.Path.cwd().parent/'sibley_38'/'info'/sessioninfo
    session_dict1 = json.load(open(path1))
    session_dict3 = json.load(open(path3))
    session_info = json.load(open(pathinfo))
    task_log = session_info['task_log']
    session_start = []
    for files in task_log:
        for i in files.items():
            if i == ('filename', 'audio/voice_speak_your_answers.mp3'):
                session_start.append(files['start'])

    cols_abs = []  # absolute time and colour stored as a tuple
    # would be nice if we could initialize this list to the right size

    #changing the first zero will give us the different versions of the transcript
    please_time1 = session_dict1['transcripts'][0]['words'][0]['start_time']
    please_time2 = session_dict1['transcripts'][0]['words'][14]['start_time']
    please_time3 = session_dict3['transcripts'][0]['words'][0]['start_time']
    please_time4 = session_dict3['transcripts'][0]['words'][14]['start_time']

    # the index of the dictionary where each word, start_time and duration are keys
    words1 = session_dict1['transcripts'][0]['words']
    words3 = session_dict3['transcripts'][0]['words']
    colors_time(words1, please_time1, please_time2, session_start[0], session_start[1], cols_abs)
    colors_time(words3, please_time3, please_time4, session_start[2], session_start[3], cols_abs)
    return cols_abs


def write_into_csv(csv_file, session1, session3, session_info):
    colors = calc_absolute_time(session1, session3, session_info)
    #csv_path = pathlib.Path.cwd().parent/'sibley_38'/'keyboard'/csv_file
    f = open(csv_file, "r")
    csv_read = csv.reader(f)
    f2 = open("speech2.csv", "w")
    csv_write = csv.writer(f2)
    rows = []
    a = 0 #index
    index = 0
    for row in csv_read:
        if a == 0 or a == 11 or a == 32 or a == 43 or a == 64 or a == 75:
            row.append("response")
        elif a < 32:
            row.append(colors[index][0])
            index += 1
        elif a < 64:
            row.append(row[4])
        else:
            row.append(colors[index][0])
            index += 1
        rows.append(row)
        a += 1
    ind = 0
    i = 0
    while i < (len(rows)):
        if rows[i][2] == "":
            rows[i][2] = colors[ind][1]
            rows[i][3] = (colors[ind][1] - float(rows[i][6]))
            ind += 1
            if i == 31:
                i += 32
        i += 1
    csv_write.writerows(rows)
    return
