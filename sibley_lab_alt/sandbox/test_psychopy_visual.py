from psychopy import visual, core
import random


def show_stimulus(win, color):
    custom_color = {'blue': '#0000FF',  # blue rgb[0, 0, 255]
                    'green': '#00FF00',  # green rgb[0, 255, 0]
                    'grey': '#6C6C6C',  # grey rgb[108, 108, 108]
                    'black': '#000000'
                    }
    text_cross = visual.TextStim(win=win, text='\u00D7', color=custom_color['black'],
                                 colorSpace='hex', height=8.6, pos=[0, 0.5])
    text_cross.draw()
    win.flip()
    core.wait(random.randint(300, 500) / 1000)
    win.flip()
    circle = visual.Circle(
        win=win,
        units="pix",
        radius=85,
        fillColor=custom_color[color],
        colorSpace='hex',
        lineWidth=0,
        pos=[0, 0]
    )
    circle.draw()
    win.flip()
    core.wait(random.randint(800, 1200) / 1000)


mywin = visual.Window(monitor="testMonitor", units="deg", fullscr=True, color=[-1, -1, -1])

show_stimulus(mywin, color='green')
mywin.close()


