import json

params = {'color_no': 6,
          'perc_mismatch': 50,
          'rounds': 20,
          'duration_text': 1.5,
          'duration_blank': 0.5,
          'keyboard_events': None}

data_capture = ['audio', 'EEG', 'keyboard', 'motion']

task = {'name': 'stroop',
        'params': params}

doc = {'session_type': 'Stroop test demo',
       'duration': 30,
       'data_capture': data_capture,
       'task': [task, task]
       }

with open('config_template/' + task['name'] + '.json', 'w') as outfile:
    json.dump(doc, outfile, indent=4)


#play_video
params = {'filename': None,
          'wait': False,
          'no_repeats': 0}

data_capture = ['audio', 'EEG', 'keyboard', 'motion']

task = {'name': 'video',
        'params': params}

doc = {'session_type': 'play video demo',
       'duration': 30,
        'data_capture': data_capture,
       'task': [task, task]
       }

with open('config_template/' + task['name'] + '.json', 'w') as outfile:
    json.dump(doc, outfile, indent=4)


# play_audio
params = {'filename': None,
          'wait': False}

data_capture = ['audio', 'EEG', 'keyboard', 'motion']

task = {'name': 'audio',
        'params': params}

doc = {'session_type': 'play audio demo',
       'duration': 30,
        'data_capture': data_capture,
       'task': [task, task]
       }

with open('config_template/' + task['name'] + '.json', 'w') as outfile:
    json.dump(doc, outfile, indent=4)


# show_image
params = {'filename': None,
          'duration': 10}

data_capture = ['audio', 'EEG', 'keyboard', 'motion']

task = {'name': 'image',
        'params': params}

doc = {'session_type': 'show image demo',
       'duration': 10,
       'task': [task, task]
       }

with open('config_template/' + task['name'] + '.json', 'w') as outfile:
    json.dump(doc, outfile, indent=4)


