import os
import time
import uuid
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mbox
from tkinter.filedialog import askopenfilename
from pylsl import resolve_byprop, resolve_stream, stream_inlet, resolve_streams
from psychopy import visual
from sibley.configuration.parser import list_session, run_session, get_data_file, get_eeg_marks
from sibley.devices.default_eeg import DefaultEEG
from sibley.devices.epoc import EPOC
from sibley.devices.muse import Muse
from sibley.task.media import record_audio, show_text
from sibley.utils import windows_process_running, windows_taskkill
from pathlib import Path
import shutil
from sibley.utils import zip_folder, fix_muse_data
import json
from PIL import ImageTk,Image
from functools import partial
from multiprocessing import Process

########################################################
# Testing Git dev branch
########################################################

# using global variable (and not class-level) to circumvent library-related issues
# specifically, marker injection fails when with class-level variable
eeg_device = None
session_started = False
# using global to improve code readability (reduces "self hell")
params = None
data_file = None  # initialized by store_settings from session config['data_capture'], using captured data types

params_default = {'study': 'unknown',
                  'session_type': 'unknown',
                  'eeg_device': 'unknown',
                  'participant_id': 'unknown',
                  'group': 'unknown',
                  'age': 'unknown',
                  'comments': 'unknown',
                  'session_uuid': 'unknown',
                  'timestamp': 'unknown',
                  'user_interface': 'muse'}

device_default = {'Session without EEG': 'none',
                       'Muse 2': 'muse2',
                       'Muse S': 'museS',
                       'EPOC X': 'EPOCX'}


def get_dict_keys(_dict):
    return list(_dict.keys())


class GuiMainMuse:

    def __init__(self):

		#Initialize some variables
        global eeg_device
        global params
        self.after_id = None # 'after' loop, needed to close it
        #eeg_device = DefaultEEG()
        eeg_device = None
        self.bluemuse_stream = None
        self.task_log = []
        self.device = device_default
        self.session_duration, self.session_config_file = list_session()

		#check whether all the required subdirectories exist, if not, create them
        folders_required = ['session_media/audio', 'session_media/images', 'session_media/video',
                            'output/audio', 'output/info', 'output/keyboard', 'output/motion', 'output/session',
                            'session_logs', 'session_config']
        folders_required += ['output/EEG/' + item for item in list(self.device.values())]
        for item in folders_required:
            os.makedirs(item, exist_ok=True)
		
		#???
        params = params_default
        params['user_interface'] = 'muse'

		#this was hardcoded to true right above since we are just trying to get muse working for the MVP
		# TO-DO: make this dynamically assigned
        if params['user_interface']=='muse':

			#execute display step 1, which is to show the instructions for putting on the headband
            self.root = Tk()
            self.root.geometry("1200x650")
            self.root.title("Sibley EEG v0.1")
            self.display_window_step01()

            eeg_device = Muse()
            eeg_device.stream_open()


            # bluemuse_stream() periodically instructs BlueMuse to start the stream from the paired device
            # the goal is to rescue dropped connections (stopped streaming in BlueMuse)
            # Function executed as multiprocess in the main loop (and not in the Muse object) to prevent interference with tkinter
            eeg_device.process_bluemuse_stream = Process(target=eeg_device.keep_bluemuse_stream)
            eeg_device.process_bluemuse_stream.start()

            # The window BlueMuse is minimized immediately to avoid causing confusion to the user
            os.system("C:\\PROGRA~1\\nircmd-x64\\nircmd.exe win hide title \"BlueMuse\"")

			#time.sleep(5) #not sure why this was here. it was delaying the popping up of the control panel.
			#the reason might have been to allow the blue muse to pop up properly. Either way, it isnt interfering with the control panel

            # The second window, BlueMuse's "LSL Bridge" takes longer to appear, but we don't know exactly when
            os.system("C:\\PROGRA~1\\nircmd-x64\\nircmd.exe win hide title \"LSL Bridge\"")

			#execute display step 2, which then displays the horseshoe, battery etc.
            self.root = Tk()
            self.root.geometry("1200x650")
            self.root.title("Sibley EEG v0.1")
            self.display_window_step02() #this step is recursive and you will not progress until they pass QC and click start session
			

			#create a data outlet? and store the settings, which were hard-coded anyway.
            eeg_device.open_outlet()
            self.store_settings()

			#start executing the actual task session
            session_started = True
            self.start_session()

			#once the session is over, go to step 3 which is to save the data
            self.root = Tk()
            self.root.geometry("1200x650")
            self.root.title("Sibley EEG v0.1")
            self.display_window_step03()

            self.save_session()
            eeg_device.stream_close() # kills: BlueMuse AND eeg_device.process_bluemuse_stream
            sys.exit()


    def store_settings(self):
        global params
        global data_file
        params['study'] = 'NeuroPilot'
        params['session_type'] = 'home_session_2209'
        params['eeg_device'] = 'Muse S'
        params['timestamp'] = time.strftime("%Y%m%d-%H%M%S")
        params['participant_id'] = 'brown_pigeon'
        data_file = get_data_file('session_config/' + self.session_config_file[params['session_type']])

        if 'audio' in data_file.keys():
            data_file['audio'] = 'output/audio/' + \
                                 params['timestamp'] + '_' + params['study'] + \
                                 '_' + params['participant_id'] + '.wav'
        if 'keyboard' in data_file.keys():
            data_file['keyboard'] = 'output/keyboard/' + \
                                    params['timestamp'] + '_' + params['study'] + \
                                    '_' + params['participant_id'] + '.csv'
            # os.open(, 'a').close()  # creates empty file, simplifies handling from different tasks
            open(str(data_file['keyboard']), mode='a').close()


    def start_session(self):
        global eeg_device
        global params
        global data_file
        print('start_session')
        print(params['eeg_device'])
        if 'audio' in data_file.keys():
            m, s = divmod(self.session_duration[params['session_type']], 60)
            record_audio(filename=data_file['audio'], until=str(m) + ':' + str(s))
        if params['eeg_device'] == 'Muse 2' or params['eeg_device'] == 'Muse S':
            data_file['EEG'] = 'output/EEG/' + self.device[params['eeg_device']] + '/' + \
                               params['timestamp'] + '_' + params['study'] + \
                               '_' + params['participant_id'] + '.csv'
            eeg_device.record_data(fn=data_file['EEG'], duration=self.session_duration[params['session_type']])

        mywin = visual.Window(monitor="testMonitor", units="deg", fullscr=True, color=[-1, -1, -1])
        self.task_log = run_session(filename='session_config/' + self.session_config_file[params['session_type']],
                                    eeg=eeg_device,
                                    win=mywin,
                                    data_file=data_file)
        show_text(win=mywin, text='Session completed:\n\n' + params['session_type'], duration=4)
        mywin.close()

    def save_session(self):
        global params
        global data_file
        print(data_file)
        #params['comments'] = self.textfield_comments.get("1.0", END)[:-1]
        params['session_uuid'] = str(uuid.uuid4())
        session_name = params['timestamp'] + '_' + params['study'] + '_' + params['participant_id']
        Path("output/session/" + session_name).mkdir(parents=True, exist_ok=True)
        session = {'params': params, 'data_file': data_file}
        if 'EEG' in data_file.keys():
            if data_file['EEG'] != 'none':
                session['EEG_marks'] = get_eeg_marks('session_config/' + self.session_config_file[params['session_type']])
        session['task_log'] = self.task_log
        with open('output/info/' + session_name + '.json', 'w') as outfile:
            json.dump(session, outfile, indent=4)
        shutil.copyfile('output/info/' + session_name + '.json', 'output/session/' + session_name + '/session_info.json')
        if 'EEG' in data_file.keys():
            if data_file['EEG'] == 'none':  # session supports EEG capture, but it was executed with "no EEG device"
                open('output/session/' + session_name + '/EEG_none.txt', mode='a').close()  # creates empty file
            else:
                if params['eeg_device'] == 'Muse 2' or params['eeg_device'] == 'Muse S':
                    fix_muse_data(data_file['EEG'])
                #data_file['EEG'] can contain one file (Muse) or multiple (EPOC)
                chunks = data_file['EEG'].split('|')
                for chunk in chunks:
                    print('copying...' + chunk)
                    filename, file_extension = os.path.splitext(chunk)
                    shutil.copyfile(chunk, 'output/session/' + session_name + '/EEG' + file_extension)
        if 'audio' in data_file.keys():
            filename, file_extension = os.path.splitext(data_file['audio'])
            print('data_file[audio]: ' + data_file['audio'])
            shutil.copyfile(data_file['audio'], 'output/session/' + session_name + '/audio' + file_extension)
        if 'keyboard' in data_file.keys():
            filename, file_extension = os.path.splitext(data_file['keyboard'])
            shutil.copyfile(data_file['keyboard'], 'output/session/' + session_name + '/keyboard' + file_extension)

        zip_folder(dir_home=os.getcwd() + '\\output',
                   dir_parent=os.getcwd() + '\\output\\session\\',
                   dir_target=session_name,
                   file_extension='sbl')
        shutil.rmtree(os.getcwd() + '\\session\\' + session_name)

        print('saving session...')
        os.chdir('../') #  restores base directory, it got switched to output/
        print(os.getcwd())

    def close_window(self, confirmation_prompt=False, sys_exit=False):
        # TO-DO: connect to close window button (right corner X)
        print('close_window')
        global eeg_device
        do_close_root = True
        if confirmation_prompt:
            result = mbox.askquestion("Exit application",
                                      "Do you want to close the program?",
                                      icon='warning')
            if result == 'no':
                do_close_root = False
        if do_close_root:
            self.root.destroy()
            if sys_exit:
                eeg_device.stream_close()
                sys.exit()


    def dialog_about(self):
        mbox.showerror('About', 'Sibley EEG v0.1 (development version')

    def display_window_step01(self):
		#This function is called during initialization of the GUI and is used to display the instructions to equip the device.
		#TO-DO: switch the instructions (hard-coded) from muse S to muse 2 for the time being.
		#TO-DO: we want to make this function dynamically figure out whether muse 2 or muse S is being used and then display the correct instructions.
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

        config_font_large = ("Helvetica", 24)
        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)

        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=c1, y=r0)
        # 'Button(command=...)' does not allow args (this triggers the action without pressing the button)
        # 'partial(func, arg1, arg2, ...)' is a workaround; lambda functions can also be used
        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=partial(self.close_window, confirmation_prompt=True, sys_exit=True), state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=c5 - 100, y=r0)

        self.label_step1 = Label(self.root, text="Step 1: prepare the headband", font=config_font_large).place(x=c3, y=r0)

        self.canvas = Canvas(self.root, width = 420, height = 400)
        self.canvas.place(x=0, y=r2)

        image1 = Image.open("session_media/images/muse_headband_install.jpg")
        test = ImageTk.PhotoImage(image1)

        label1 = Label(image=test)
        label1.place(x=0, y=r2)


        self.label_start_session = Label(self.root, text="When ready, press ----- >", font=config_font).place(x=c1, y=r9)
        self.button_start_session = Button(self.root, text="Next", font=config_font_medium, width=15,
                                           height=1,
                                           command=self.root.destroy, state=NORMAL, bg='green')
        self.button_start_session.place(x=c3, y=r9)
        self.root.mainloop()


    def display_window_step02(self):
		#This is to display the quality testing screen that displays the horseshoe, battery etc.
		#It will loop back to itself every N=1000 miliseconds until you break the loop by passing the quality 
		#check and clicking "start session"
        global eeg_device
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

        config_font_large = ("Helvetica", 24)
        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)

        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=c1, y=r0)

        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=partial(self.close_window, confirmation_prompt=True, sys_exit=True), state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=c5 - 100, y=r0)

        self.label_muse_status = Label(self.root, text="Muse headband status:", font=config_font).place(x=c1, y=r2)
        self.label_muse_status_msg = Label(self.root, text="", font=config_font)
        self.label_muse_status_msg.place(x=c3, y=r2)
        self.label_muse_status_msg.config(text='No connection', fg='red')

        self.label_muse_battery = Label(self.root, text="Muse headband battery:", font=config_font).place(x=c1, y=r3)
        self.label_muse_battery_msg = Label(self.root, text="", font=config_font)
        self.label_muse_battery_msg.place(x=c3, y=r3)
        self.label_muse_battery_msg.config(text='- - -', fg='black')

        self.label_eeg_qc = Label(self.root, text="EEG quality check:", font=config_font).place(x=c1, y=r4)
        self.label_eeg_qc_msg = Label(self.root, text="", font=config_font)
        self.label_eeg_qc_msg.place(x=c3, y=r4)
        self.label_eeg_qc_msg.config(text='- - -', fg='black')


        self.label_start_session = Label(self.root, text="Session", font=config_font).place(x=c1, y=r9)
        self.button_start_session = Button(self.root, text="Start session", font=config_font_medium, width=15,
                                           height=1,
                                           command=self.close_window, state=DISABLED, bg='grey')
        self.button_start_session.place(x=c3, y=r9)

        self.label_step1 = Label(self.root, text="Step 2: establish data link", font=config_font_large).place(x=c3, y=r0)

        self.canvas = Canvas(self.root, width = 420, height = 400)
        self.canvas.create_rectangle(2, 10, 380, 380)
        self.canvas.place(x=720, y=150)

        # Image.open (from PIL) handles more image formats than the default PhotoImage (can open certain types directly)
        self.image1_pre = Image.open("session_media/images/horseshoe_n_n_n_n.png")
        self.image1 = ImageTk.PhotoImage(self.image1_pre)
        self.label_horseshoe = Label(image=self.image1)
        self.label_horseshoe.place(x=800, y=250)

        self.label_horseshoe = Label(self.root, text="EEG sensor status", font=config_font).place(x=c4-35, y=r2)
        self.label_horseshoe_msg = Label(self.root, text="", font=config_font)
        self.label_horseshoe_msg.place(x=c4-60, y=r5-40)
        self.label_horseshoe_msg.config(text ='                    - - -        ', fg='black', font=config_font_medium)


        self.root.lift()
        #self.root.attributes('-topmost', True)
        #self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.after(1000, self.update_gui_muse())
        self.root.mainloop()


    def update_gui_muse(self):
        print('update_gui_muse...')
        global eeg_device

        eeg_device.update_status_telemetry()

        print(eeg_device.status)
        if eeg_device.status['is_connected']==True:
            self.label_muse_status_msg.config(text="Connected", fg='green')
            self.label_muse_battery_msg.config(text=str(eeg_device.status['battery_level']), fg='green')

            eeg_device.update_status_channel_qc()

            self.image1_pre = Image.open('session_media/images/horseshoe_' + eeg_device.status['channel_summary'] + '.png')
            self.image1 = ImageTk.PhotoImage(self.image1_pre)
            self.label_horseshoe = Label(image=self.image1)
            self.label_horseshoe.place(x=800, y=250)

            if eeg_device.status['channel_summary'] == 'g_g_g_g':
                self.label_eeg_qc_msg.config(text='Pass', fg='green')
                self.label_horseshoe_msg.config(text='          Good signal              ', fg='green')
                self.button_start_session.config(state=NORMAL, bg='green')
            else:
                self.label_eeg_qc_msg.config(text='Fail', fg='red')
                self.label_horseshoe_msg.config(text='         Adjust headband          ', fg='red')
                self.button_start_session.config(state=DISABLED, bg='grey')
				
        if session_started==False:
            self.root.after(1000, self.update_gui_muse)

    def display_window_step03(self):

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

        config_font_large = ("Helvetica", 24)
        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)

        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=c1, y=r0)

        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=partial(self.close_window, confirmation_prompt=False, sys_exit=False), state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=c5 - 100, y=r0)

        self.label_step1 = Label(self.root, text="Step 3: session complete", font=config_font_large).place(x=c3, y=r0)

        self.canvas = Canvas(self.root, width = 420, height = 400)
        self.canvas.place(x=0, y=r2)

        image1 = Image.open("session_media/images/muse_headband_end_ok.jpg")
        test = ImageTk.PhotoImage(image1)

        label1 = Label(image=test)
        label1.place(x=c2-70, y=r2)


        #self.label_start_session = Label(self.root, text="When ready, press ----- >", font=config_font).place(x=c1, y=r9)
        self.button_start_session = Button(self.root, text="Close program", font=config_font_medium, width=15,
                                           height=1,
                                           command=partial(self.close_window, confirmation_prompt=False, sys_exit=False), state=NORMAL, bg='green')
        self.button_start_session.place(x=c3, y=r9)

        self.root.mainloop()



