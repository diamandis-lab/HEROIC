import os
import time
from datetime import datetime
from glob import glob
from random import choice
import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event


#from eegnb.stimuli import CAT_DOG
CAT_DOG = 'session_media/images/p300_visual'

# Stay still, focus on the centre of the screen, and try not to blink.

def run_session(win=None, duration=90, eeg=None, save_fn=None):
    n_trials = 2010
    iti = 0.4
    soa = 0.7
    jitter = 0.2
    record_duration = np.float32(duration)
    markernames = [1, 2, 999]

    # Setup trial list
    image_type = np.random.binomial(1, 0.5, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=win, image=fn)

    targets = list(map(load_image, glob(os.path.join(CAT_DOG, "target-*.jpg"))))
    nontargets = list(map(load_image, glob(os.path.join(CAT_DOG, "nontarget-*.jpg"))))

    start = time.time()
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select and display image
        label = trials["image_type"].iloc[ii]
        image = choice(targets if label == 1 else nontargets)
        image.draw()
        win.flip()
        timestamp = time.time()

        if eeg:
            # muselsl accept other backends, then 'marker = mark' (without parenthesis)
            eeg.outlet.push_sample(x=[markernames[label]], timestamp=timestamp)
        print(str(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')) + " mark: " + str(markernames[label]))


        # offset
        core.wait(soa)
        win.flip()
        if (time.time() - start) > record_duration:
            break

        event.clearEvents()

#win = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
#run_session(duration=10, win=mywin)
#mywin.close()