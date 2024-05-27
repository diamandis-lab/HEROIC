import subprocess
from playsound import playsound
from psychopy import core, visual


def play_video_internal(win, filename, no_repeats=0):
    # psychopy MovieStrim3 (moviepy backend), displays video in psychopy window
    # audio doesn't work due to configuration problem in Windows
    mov = visual.MovieStim3(win, 'session_media/' + filename, noAudio=True)
    for x in range(0, no_repeats + 1):
        while mov.status != visual.FINISHED:
            mov.draw()
            win.flip()
        mov.seek(0)
        mov.status = visual.NOT_STARTED


def play_video_vlc(filename, wait=False, no_repeats=0):

    cmd = ['C:/Program Files (x86)/VideoLAN/VLC/vlc.exe',
           '--video-on-top',
           '--fullscreen',
           '--no-video-title',
           '--intf',
           'dummy',
           '--dummy-quiet',
           '--input-repeat', str(no_repeats),
           '--play-and-exit',
           'session_media/' + filename]
    # 'wait' and 'shell' are opposite
    #subprocess.call(cmd, shell=not wait)
    subprocess.call(cmd, shell=False)


def show_image(win, filename, duration):
    image = visual.ImageStim(win=win, image='session_media/' + filename)
    image.draw()
    win.flip()
    core.wait(duration)
    win.flip()


def show_text(win, text, duration, height=2, wrap_width=32):
    text_stim = visual.TextStim(win=win, text=text, height=height, wrapWidth=wrap_width)
    text_stim.draw()
    win.flip()
    core.wait(duration)
    win.flip()


def play_sound(filename, wait=False):
    playsound('session_media/' + filename, block=wait)


def record_audio(filename, until):
    cmd = ['C:/Program Files (x86)/fmedia/fmedia.exe',
           '--record', '--background',
           '--volume=80',
           '--until=' + until,
           '--out=' + filename,
           '--rate=16000',
           '--channels=mono']
    print(cmd)
    subprocess.call(cmd, shell=True)


