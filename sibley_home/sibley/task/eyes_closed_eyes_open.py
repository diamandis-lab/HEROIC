from psychopy import visual, core, event
import random
import time


def run_session(win=None, eeg=None, rounds=60, condition='closed'):
    custom_color = {'grey': '#6C6C6C',  # grey rgb[108, 108, 108]
                    'black': '#000000'
                    }

    mark = {'closed': 3,
            'open': 4}

    if condition == 'closed':
        cross_color = 'grey'
    else:
        cross_color = 'black'

    def show_cross(win):
        
        text_cross = visual.TextStim(win=win, text='\u00D7', color=custom_color[cross_color],     colorSpace='hex', height=8.6, pos=[0, 0.5])
        text_cross.draw()
        win.flip()
        core.wait(1) # 1 second?
        win.flip()

    def show_stimulus(win, color):
        
        #circle = 
        #circle.draw()
        win.flip()
        core.wait(random.randint(800, 1200) / 1000)

    win.color = custom_color['grey']  # sets the background color for the task
    win.flip()

    for pos in range(0, rounds): # or duration, where every wait time (1) is printed/pushed sample

        if condition == 'closed':
            condition_curr = 'closed'
        else:
            condition_curr = 'open'
        print('round=' + str(pos) + ' condition =' + condition_curr)
        show_cross(win)
        
        if eeg:
            eeg.outlet.push_sample(x=[mark[condition_curr]], timestamp=time.time())
    #show_stimulus(win=win, color=color_curr)

    win.color = custom_color['black']  # restores default background color
    win.flip()