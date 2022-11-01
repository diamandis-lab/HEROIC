import os

import pygame as pg
import time

import winsound

winsound.Beep(500,1)

pg.mixer.init(frequency=16000, size=-16, channels=2, buffer=4096) # setup mixer to avoid sound lag
#pg.mixer.init()
pg.mixer.set_num_channels(50)
#pg.init()

#pg.mixer.music.load("session_media\\audio\\test\\sin_100Hz_-20dBFS_10s.wav")
#pg.mixer.music.play(-1)

#background = pg.mixer.Sound("session_media\\audio\\test\\sin_100Hz_-20dBFS_10s.wav")
#background.play()
a1Note = pg.mixer.Sound("session_media\\audio\\test\\sin_440Hz_-3dBFS_0.2s.wav")
a2Note = pg.mixer.Sound("session_media\\audio\\test\\sin_660Hz_-3dBFS_0.2s.wav")
for i in range(10):
    a1Note.play()
    time.sleep(0.5)
    a2Note.play()
    time.sleep(0.5)




for i in range(10):
    a1Note.play()
    time.sleep(0.5)
    a2Note.play()
    time.sleep(0.5)


pg.mixer.set_num_channels(50)

for i in range(25):
    a1Note.play()
    time.sleep(0.3)
    a2Note.play()
    time.sleep(0.3)


#pg.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag

#pg.mixer.pre_init()

#then instantiate and start your controller
pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
pg.mixer.init()

#then in your button click or wherever
pg.mixer.music.load("session_media\\audio\\test\\wavTones.com.unregistred.sin_440Hz_-6dBFS_0.2s.wav")
pg.mixer.music.play(-1)

time.sleep(10)
pg.mixer.music.pause()


