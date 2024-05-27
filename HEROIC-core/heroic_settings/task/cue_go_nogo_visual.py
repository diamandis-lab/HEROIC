from psychopy import visual, core, event
import random
import time
import pandas as pd


def run_session(win=None, eeg=None, keyboard_logfile=None, no_trials=60):

    stim_rgb = [1, 1, 1]
    rect = visual.Rect(
        win=win,
        units="pix",
        width=124,
        height=124,
        fillColor=stim_rgb,
        pos=[0, 0]
    )

    text_plus = visual.TextStim(win=win, text='+', color=stim_rgb, height=7.8, pos=[0, 0.4])
    text_cross = visual.TextStim(win=win, text='\u00D7', color=stim_rgb, height=8.6, pos=[0, 0.5])

    trial_clock = core.Clock()
    keystrokes = pd.DataFrame(columns=['test_type', 'key', 'timestamp_stim', 'time_stim_response', 'stim_type'])
    duration_stim = 2.65

    stim_name = {1: 'Go',
                 2: 'Nogo',
                 3: 'Cue'}

    for r in range(no_trials):
        timestamp_cue = time.time()
        if eeg:
            # muselsl accept other backends, then 'marker = mark' (without parenthesis)
            eeg.outlet.push_sample(x=[3], timestamp=timestamp_cue)
        rect.draw()
        win.flip()
        core.wait(0.150)
        win.flip()
        core.wait(1 + random.randint(0, 1000) / 1000)
        mark = random.getrandbits(1) + 1  # 1 ('go') or 2 ('nogo'), random selection
        timestamp_stim = time.time()
        if eeg:
            eeg.outlet.push_sample(x=[mark], timestamp=timestamp_stim)

        if mark == 1:  # 'Go' signal
            text_cross.draw()
            win.flip()
        else:  # 'NoGo' signal
            text_plus.draw()
            win.flip()

        if keyboard_logfile:
            event.clearEvents()
            trial_clock.reset()
            core.wait(0.150, hogCPUperiod=0.150)
            win.flip()
            core.wait(2.5, hogCPUperiod=2.5)
            key_pressed = event.getKeys(timeStamped=trial_clock)
            if len(key_pressed) > 0:
                key_pressed = key_pressed[0]
            else:
                key_pressed = ["none", -1]

            keyboard_event = {'test_type': 'cue_go_nogo_visual',
                              'key': key_pressed[0],
                              'timestamp_stim': timestamp_stim,
                              'time_stim_response': key_pressed[1],
                              'stim_type': stim_name[mark]}
            keystrokes = keystrokes.append(keyboard_event, ignore_index=True)
        else:
            core.wait(0.150)
            win.flip()
            core.wait(2.5)

    keystrokes.to_csv(keyboard_logfile, mode='a', index=False)




#win = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True, color=[1,1,1])
#run_session(win=win, keyboard_logfile='keyboard_cue_go_nogo-visual.txt',no_trials=10)
#win.close()


