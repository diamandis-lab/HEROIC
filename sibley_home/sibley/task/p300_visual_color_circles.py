from psychopy import visual, core, event
import random
import time


def run_session(win=None, eeg=None, rounds=40, percent_green=90):
    custom_color = {'blue': '#0000FF',  # blue rgb[0, 0, 255]
                    'green': '#00FF00',  # green rgb[0, 255, 0]
                    'grey': '#6C6C6C',  # grey rgb[108, 108, 108]
                    'black': '#000000'
                    }

    mark = {'green': 1,
            'blue': 2}

    def show_cross(win):
        text_cross = visual.TextStim(win=win, text='\u00D7', color=custom_color['grey'],     colorSpace='hex', height=8.6, pos=[0, 0.5])
        text_cross.draw()
        win.flip()
        core.wait(random.randint(300, 500) / 1000)
        win.flip()

    def show_stimulus(win, color):
        
        circle = visual.Circle(
            win=win,
            units="pix",
            radius=100,
            fillColor=custom_color[color],
            colorSpace='hex',
            lineWidth=0,
            pos=[0, 0]
        )
        circle.draw()
        win.flip()
        core.wait(random.randint(800, 1200) / 1000)

    win.color = custom_color['grey']  # sets the background color for the task
    win.flip()

    for pos in range(0, rounds):
        if random.randint(1, 100) > int(percent_green):
            color_curr = 'blue'
        else:
            color_curr = 'green'
        print('round=' + str(pos) + ' color=' + color_curr)
        show_cross(win)
        
        if eeg:
            eeg.outlet.push_sample(x=[mark[color_curr]], timestamp=time.time())
        show_stimulus(win=win, color=color_curr)

    win.color = custom_color['black']  # restores default background color
    win.flip()



#win = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True, color=[1,1,1])
#run_session(win=win, eeg=None, no_trials=40)
#win.close()





