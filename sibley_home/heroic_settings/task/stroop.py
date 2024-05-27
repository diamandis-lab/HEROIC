from psychopy import visual, core, event
import time
import pandas as pd
from random import randint, shuffle
import inspect


def run_session(eeg=None, win=None,
           color_no=6, perc_mismatch=50, rounds=20,
           duration_text=1.5, duration_blank=0.5,
           keyboard_logfile=None, params_list=None):
    if params_list:
        if 'color_no' in params_list:
            color_no = params_list['color_no']
        if 'perc_mismatch' in params_list:
            perc_mismatch = params_list['perc_mismatch']
        if 'rounds' in params_list:
            rounds = params_list['rounds']
        if 'duration_text' in params_list:
            duration_text = params_list['duration_text']
        if 'duration_blank' in params_list:
            duration_blank = params_list['duration_blank']
        if 'keyboard_logfile' in params_list:
            keyboard_logfile = params_list['keyboard_logfile']

    color_series = _build_color_series(color_no=color_no, perc_mismatch=perc_mismatch, rounds=rounds)

    color_rgb = {'blue': [0, 32, 255],
                 'green': [0, 192, 0],
                 'pink': [255, 96, 208],
                 'red': [255, 0, 0],
                 'white': [255, 255, 255],
                 'yellow': [255, 255, 40]}
    word_pos = {'blue': [0, 0],
                'green': [-2, 0],
                'pink': [0, 0],
                'red': [0, 0],
                'white': [-2, 0],
                'yellow': [-3, 0]}

    trial_clock = core.Clock()
    keystrokes = pd.DataFrame(columns=['type', 'key', 'timestamp', 'time_delay', 'word_color', 'word_text'])

    for s in range(len(color_series)):
        word_text = color_series['text'][s]
        word_color = color_series['color'][s]
        if word_text == word_color:
            mark = 1
        else:
            mark = 2

        word = visual.TextStim(win=win, text=word_text, color=color_rgb[word_color], height=8, pos=word_pos[word_text],
                               colorSpace='rgb255')
        word.draw()
        timestamp = time.time()
        if eeg:
            # muselsl accept other backends, then 'marker = mark' (without parenthesis)
            eeg.outlet.push_sample(x=[mark], timestamp=timestamp)
        win.flip()
        if keyboard_logfile:
            event.clearEvents()
            trial_clock.reset()
            core.wait(duration_text, hogCPUperiod=duration_text)
            key_pressed = event.getKeys(timeStamped=trial_clock)
            if len(key_pressed) > 0:
                key_pressed = key_pressed[0]
            else:
                key_pressed = ["none", -1]

            if word_text == word_color:
                keystroke_type = 'concordant'
            else:
                keystroke_type = 'discordant'
            keyboard_event = {'type': keystroke_type, 'key': key_pressed[0], 'timestamp_stim': timestamp,
                              'time_delay': key_pressed[1], 'word_color': word_color, 'word_text': word_text}
            keystrokes = keystrokes.append(keyboard_event, ignore_index=True)
        else:
            core.wait(duration_text)

        win.flip()
        core.wait(duration_blank)
    keystrokes.to_csv(keyboard_logfile, mode='a', index=False)


def _build_color_series(color_no=6, perc_mismatch=50, rounds=20):
    colorname = None
    if color_no == 6:
        colorname = ['blue', 'green', 'pink', 'red', 'white', 'yellow']

    if color_no == 3:
        colorname = ['green', 'yellow', 'red']

    series_word_color = list()
    word_color_last = None
    for r in range(rounds):
        word_color = word_color_last
        while word_color == word_color_last:
            word_color = colorname[randint(0, len(colorname) - 1)]
        series_word_color.append(word_color)
        word_color_last = word_color

    m1 = [False] * int(rounds * perc_mismatch / 100)
    m2 = [True] * (rounds - int(rounds * perc_mismatch / 100))
    is_match = [*m1, *m2]
    shuffle(is_match)
    is_match = is_match[0:rounds]  # just in case is larger due to rounding

    series_word_text = list()
    word_text_last = None
    for r in range(rounds):
        word_text = word_text_last
        if is_match[r]:
            word_text = series_word_color[r]
        else:
            while word_text == word_text_last:
                colorname_sub = list(colorname)  # list conversion prevents modification of 'colorname' by 'remove'
                colorname_sub.remove(series_word_color[r])
                # word_text = "other_"+colorname_sub[randint(0, len(colorname_sub)-1)]
                word_text = colorname_sub[randint(0, len(colorname_sub) - 1)]
        series_word_text.append(word_text)
        word_text_last = word_text
    # trying to avoid consecutive word_text, but still there is a case where it can happen:
    # a mismatch is randomly set, and the following is a matched, with identical word_text
    # this needs fixing
    return pd.DataFrame({'color': series_word_color, 'text': series_word_text})
