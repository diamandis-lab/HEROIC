import os
import time
from datetime import datetime
from glob import glob
from random import choice, randint
import numpy as np
from pandas import DataFrame
from playsound import playsound
from psychopy import visual, core, event


# Stay still, focus on the centre of the screen, and try not to blink.
def run_session(win=None, eeg=None, rounds=50):
    sound_standard = 'sin_440Hz_200ms'
    sound_target = 'sin_660Hz_200ms'

    sound_novel = ['1-59513-A-0_200ms', '1-85362-A-0_200ms', '1-97392-A-0_200ms', '1-100032-A-0_200ms',
                   '3-157615-A-10_200ms', '5-195710-A-10_200ms', '5-202898-A-10_200ms', '5-203739-A-10_200ms',
                   '1-42139-A-38_200ms', '2-88724-A-38_200ms', '2-127108-A-38_200ms', '5-210571-A-38_200ms',
                   '1-13571-A-46_200ms', '1-22804-A-46_200ms', '5-201170-A-46_200ms', '5-204741-A-46_200ms']

    def select_stim_type():
        pos = randint(0, 100)
        if pos < 10:
            stim_type = 'target'
        else:
            if pos < 20:
                stim_type = 'novel'
            else:
                stim_type = 'standard'
        return (stim_type)

    def get_sound(stim_type):
        if stim_type == 'standard':
            sound = sound_standard
        if stim_type == 'target':
            sound = sound_target
        if stim_type == 'novel':
            pos = randint(0, len(sound_novel) - 1)
            sound = sound_novel[pos]
        return (sound)

    markernames = {'standard': 1, 'target': 2, 'novel': 3} # this should be loaded from config.json!!!
    list_stim_type = []
    for n in range(rounds):
        stim_type = select_stim_type()
        list_stim_type.append(stim_type)
        sound = get_sound(stim_type)
        fname = 'session_media/auditory_oddball/audio/' + sound + '.wav'

        timestamp = time.time()
        if eeg:
            # muselsl accept other backends, then 'marker = mark' (without parenthesis)
            eeg.outlet.push_sample(x=[markernames[stim_type]], timestamp=timestamp)
        print(str(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')) + " mark: " + str(markernames[stim_type]))

        playsound(fname, block=False)
        time_interval = randint(700, 1200) / 1000
        print(stim_type + '...' + sound + '...' + str(time_interval))
        time.sleep(time_interval)


