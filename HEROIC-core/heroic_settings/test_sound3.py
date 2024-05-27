from playsound import playsound
import time
import random


sound_standard = 'sin_440Hz_200ms'
sound_target = 'sin_660Hz_200ms'

sound_novel = ['1-59513-A-0_200ms','1-85362-A-0_200ms','1-97392-A-0_200ms','1-100032-A-0_200ms',
               '3-157615-A-10_200ms','5-195710-A-10_200ms','5-202898-A-10_200ms','5-203739-A-10_200ms',
               '1-42139-A-38_200ms','2-88724-A-38_200ms','2-127108-A-38_200ms','5-210571-A-38_200ms',
               '1-13571-A-46_200ms','1-22804-A-46_200ms','5-201170-A-46_200ms','5-204741-A-46_200ms']


def select_stim_type():
    pos = random.randint(0, 100)
    if pos<15:
        stim_type = 'target'
    else:
        if pos <30:
            stim_type = 'novel'
        else:
            stim_type = 'standard'
    return(stim_type)

def get_sound(stim_type):
    if stim_type=='standard':
        sound=sound_standard
    if stim_type=='target':
        sound=sound_target
    if stim_type=='novel':
        pos = random.randint(0, len(sound_novel)-1)
        sound=sound_novel[pos]
    return(sound)

list_stim_type = []
for n in range(40):
    stim_type = select_stim_type()
    if len(list_stim_type)>1:
        while (list_stim_type[len(list_stim_type)-1]==stim_type) and (list_stim_type[len(list_stim_type)-2]==stim_type):
            stim_type = select_stim_type()
    list_stim_type.append(stim_type)
    sound = get_sound(stim_type)
    fname = 'session_media/audio/test/' + sound + '.wav'
    playsound(fname, block=False)
    time_interval = random.randrange(700, 1200) / 1000
    print(stim_type + '...' + sound + '...' + str(time_interval))
    time.sleep(time_interval)







