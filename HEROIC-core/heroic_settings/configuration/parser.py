import json
import subprocess
from subprocess import Popen
import time

import heroic_settings.task.stroop
import heroic_settings.task.p300_visual
import heroic_settings.task.auditory_oddball
import heroic_settings.task.cue_go_nogo_visual
import heroic_settings.task.p300_visual_color_circles
import heroic_settings.task.eyes_closed_eyes_open

from heroic_settings.task.media import play_sound, play_video_vlc, show_image, show_text
import os

task_codes = {'session_start': 90,
              'session_end': 91,
              'stroop': 80,
              'p300_visual': 81,
              'cue_go_nogo_visual': 82,
              'auditory_oddball': 83,
              'P300 visual color circles': 84,
              'eyes_closed_eyes_open': 85,
              'text': 70,
              'image': 71,
              'audio': 72,
              'video': 73}


def list_session():
    files_json = os.listdir('session_config/')
    session_duration = {}
    session_file = {}
    for filename in files_json:
        config = json.load(open('session_config/' + filename))
        session_duration[config['session_type']] = config['duration']
        session_file[config['session_type']] = filename
    return session_duration, session_file


def get_data_file(filename):
    config = json.load(open(filename))
    data_file = {}
    for item in config['data_capture']:
        data_file[item] = 'none'
    return data_file


def get_eeg_marks(filename):
    session_config = json.load(open(filename))
    dat = {}
    if 'EEG_marks' in session_config.keys():
        dat['EEG_markers'] = session_config['EEG_marks']
    else:
        dat['EEG_markers'] = None
    return dat


def run_session(filename, eeg, win, data_file):
    config = json.load(open(filename))
    task_log = []
    show_text(win=win, text='Launching session:\n\n' + config['session_type'], duration=5)

    if eeg:
        eeg.outlet.push_sample(x=[task_codes['session_start']], timestamp=time.time())
        time.sleep(1)  # needed to time-space two consecutive markers. If millisecond-close, the second can be missed

    for task in config['task']:
        time_start = time.time()
        if eeg:
            eeg.outlet.push_sample(x=[task_codes[task['name']]], timestamp=time_start)
        _run_task(eeg, win, data_file, task)
        event = {'name': task['name'],
                 'start': time_start,
                 'end': time.time()}
        if 'filename' in task['params']:
            event['filename'] = task['params']['filename']
        task_log.append(event)
        print(event)
        if eeg:
            eeg.outlet.push_sample(x=[task_codes[task['name']] + 1000], timestamp=time_start)
    if eeg:
        eeg.outlet.push_sample(x=[task_codes['session_end']], timestamp=time.time())
    return task_log


def _run_task(eeg, win, data_file, task):

    if task['name'] == 'stroop':
        print('_run_task.stroop: ')
        if data_file['keyboard'] != 'none':
            task['params']['keyboard_logfile'] = data_file['keyboard']
        sibley.task.stroop.run_session(eeg=eeg, win=win, params_list=task['params'])

    if task['name'] == 'video':
        print('_run_task.video: ' + task['params']['filename'])
        play_video_vlc(filename=task['params']['filename'], wait=task['params']['wait'],
                       no_repeats=task['params']['no_repeats'])
        #play_video_internal(win, filename=task['params']['filename'],
        #                    no_repeats=task['params']['no_repeats'])

    if task['name'] == 'audio':
        print('_run_task.sound: ' + task['params']['filename'])
        play_sound(filename=task['params']['filename'], wait=task['params']['wait'])

    if task['name'] == 'image':
        print('_run_task.image: ' + task['params']['filename'])
        show_image(win=win, filename=task['params']['filename'], duration=task['params']['duration'])

    if task['name'] == 'text':
        # printing unicode to Windows command prompt requires specific environment configuration (python interpreter)
        # replaces unicode with ascii
        print('_run_task.text: ' + str(task['params']['text'].encode('ascii', 'replace')))
        show_text(win=win, text=task['params']['text'],
                  duration=task['params']['duration'],
                  height=task['params']['height'],
                  wrap_width=task['params']['wrap_width'])

    if task['name'] == 'speech_recognition':
        print('_run_task.speech_recognition')
        cmd = ['python', 'sibley/task/speech_recognition_stream.py']
        t_start = time.time()
        with Popen(cmd, shell=True) as process:
            for s in range(10):
                time.sleep(1)
                if time.time() - t_start > 10:
                    print("terminating speech recognition...")
                    subprocess.run('taskkill /F /PID ' + str(process.pid))

    if task['name'] == 'p300_visual':
        print('_run_task.p300_visual')
        sibley.task.p300_visual.run_session(win=win, eeg=eeg, duration=task['params']['duration'])

    if task['name'] == 'auditory_oddball':
        print('_run_task.auditory_oddball')
        sibley.task.auditory_oddball.run_session(win=win, eeg=eeg, rounds=task['params']['rounds'])

    if task['name'] == 'cue_go_nogo_visual':
        print('_run_task.cue_go_nogo_visual')
        sibley.task.cue_go_nogo_visual.run_session(win=win, eeg=eeg,
                                                   keyboard_logfile=data_file['keyboard'],
                                                   no_trials=task['params']['no_trials'])

    if task['name'] == 'P300 visual color circles':
        print('_run_task.p300_visual_color_circles')
        sibley.task.p300_visual_color_circles.run_session(win=win, eeg=eeg,
                                                          rounds=task['params']['rounds'],
                                                          percent_green=task['params']['percent_green'])
    
    if task['name'] == 'eyes_closed_eyes_open':
        print('_run_task.eyes_closed_eyes_open')
        sibley.task.eyes_closed_eyes_open.run_session(win=win, eeg=eeg,
                                                          rounds=task['params']['rounds'],
                                                          condition=task['params']['condition'])








