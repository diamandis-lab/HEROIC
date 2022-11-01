
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


def calc_absolute_time(session1, session3, sessioninfo, folder_name):
    #path1 = pathlib.Path(session1)
    path1 = pathlib.Path.cwd()/folder_name/session1
    #path3 = pathlib.Path(session3)
    path3 = pathlib.Path.cwd()/folder_name/session3
    pathinfo = pathlib.Path.cwd()/folder_name/sessioninfo
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
    words1 = session_dict1['transcripts'][0]['words']
    words3 = session_dict3['transcripts'][0]['words']
    for m in range(len(words1)):
        if words1[m]['word'] == 'please' and words1[m]['start_time'] < 20.0:
            please_time1 = words1[m]['start_time']
        elif words1[m]['word'] == 'please' and words1[m]['start_time'] > 20.0:
            please_time2 = words1[m]['start_time']

    for n in range(len(words1)):
        if words3[n]['word'] == 'please' and words3[n]['start_time'] < 20.0:
            please_time3 = words3[n]['start_time']
        elif words3[n]['word'] == 'please' and words1[n]['start_time'] > 20.0:
            please_time4 = words3[n]['start_time']

    # the index of the dictionary where each word, start_time and duration are keys

    colors_time(words1, please_time1, please_time2, session_start[0], session_start[1], cols_abs)
    colors_time(words3, please_time3, please_time4, session_start[2], session_start[3], cols_abs)
    return cols_abs

print(calc_absolute_time("20210506-212721_default_racoon-deepspeech-stroop1.json", "20210506-212721_default_racoon-deepspeech-stroop3.json", "session_info.json","20210506-212721_default_racoon"))

def write_into_csv(session1, session3, session_info, folder_name):
    colors = calc_absolute_time(session1, session3, session_info, folder_name)
    path_csv = pathlib.Path.cwd()/folder_name/"keyboard.csv"
    #the keyboard file is always called keyboard
    f = open(path_csv, "r")
    csv_read = csv.reader(f)
    f2 = open(folder_name+"/"+folder_name+"_results.csv", "w")
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
            if row[1] == "left":
                row.append("green")
            elif row[1] == "down":
                row.append("yellow")
            elif row[1] == "right":
                row.append("red")
            else:
                row.append("none")
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
            #current factor callibration
            rows[i][3] = (colors[ind][1] - float(rows[i][6]))
            ind += 1
            if i == 31:
                i += 32
        i += 1
    csv_write.writerows(rows)
    return

write_into_csv("session1.json", "session3.json", "session_info.json", "20210514-152935_default_white-horse")
#write_into_csv("20210506-212721_default_racoon-deepspeech-stroop1.json", "20210506-212721_default_racoon-deepspeech-stroop3.json", "session_info.json", "20210506-212721_default_racoon")