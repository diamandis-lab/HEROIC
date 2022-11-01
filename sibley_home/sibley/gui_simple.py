import os
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mbox
import json
from PIL import ImageTk,Image


class GuiSimple:

    def __init__(self):
        self.root = Tk()
        self.root.geometry("1200x650")
        self.root.title("Sibley EEG v0.1")
        self.display_window_muse()

    def dialog_about(self):
        mbox.showerror('About', 'Sibley EEG v0.1 (development version')

    def start_session(self):
        mbox.showerror('Start', 'The session is starting...')

    def close_window(self):
        self.root.destroy()

    def display_window_muse(self):

        c1 = 20
        c2 = 220
        c3 = 350
        c4 = 820
        c5 = 1085
        r0 = 20
        r1 = 100
        r2 = 200
        r3 = 300
        r4 = 400
        r5 = 500
        r6 = 100
        r7 = 100
        r8 = 100
        r9 = 575

        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)

        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=c1, y=r0)

        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=self.close_window, state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=c5 - 100, y=r0)

        self.label_muse_status = Label(self.root, text="Muse headband status:", font=config_font).place(x=c1, y=r2)
        self.label_muse_status_msg = Label(self.root, text="Connected", font=config_font)
        self.label_muse_status_msg.place(x=c3, y=r2)
        self.label_muse_status_msg.config(text='Connected', fg='green')

        self.label_muse_battery = Label(self.root, text="Muse headband battery:", font=config_font).place(x=c1, y=r3)
        self.label_muse_battery_msg = Label(self.root, text="", font=config_font)
        self.label_muse_battery_msg.place(x=c3, y=r3)
        self.label_muse_battery_msg.config(text='OK (82%)', fg='green')

        self.label_eeg_qc = Label(self.root, text="EEG quality check:", font=config_font).place(x=c1, y=r4)
        self.label_eeg_qc_msg = Label(self.root, text="", font=config_font)
        self.label_eeg_qc_msg.place(x=c3, y=r4)
        self.label_eeg_qc_msg.config(text='Pass', fg='green')


        self.label_start_session = Label(self.root, text="Session", font=config_font).place(x=c1, y=r9)
        self.button_start_session = Button(self.root, text="Start session", font=config_font_medium, width=15,
                                           height=1,
                                           command=self.start_session, state=NORMAL, bg='green')
        self.button_start_session.place(x=c3, y=r9)





        self.canvas = Canvas(self.root, width = 420, height = 400)

        #self.canvas.create_line(300, r2, 900, r2)


        #self.canvas.create_line(2, 10, 2, 400)
        self.canvas.create_rectangle(2, 10, 380, 380)
        self.canvas.place(x=720, y=150)

        image1 = Image.open("../session_media/images/horseshoe_g_g_g_g.png")
        test = ImageTk.PhotoImage(image1)

        label1 = Label(image=test)

        label1.place(x=800, y=250)

        self.label_eeg_qc = Label(self.root, text="EEG sensor status", font=config_font).place(x=c4-35, y=r2)
        self.label_eeg_qc_msg = Label(self.root, text="", font=config_font)
        self.label_eeg_qc_msg.place(x=c4-60, y=r5-40)
        self.label_eeg_qc_msg.config(text='4 sensors are capturing good data', fg='green', font=config_font_medium)

        self.root.mainloop()



if __name__ == '__main__':
    GuiMain()
