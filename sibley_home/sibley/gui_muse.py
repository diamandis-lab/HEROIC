import os
import time
import uuid
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mbox
from tkinter.filedialog import askopenfilename
from pathlib import Path
import shutil
import json
import glob
from PIL import ImageTk,Image
from functools import partial
from multiprocessing import Process
from threading import Thread

from pylsl import resolve_byprop, resolve_stream, stream_inlet, resolve_streams
from psychopy import visual
from sibley.configuration.parser import list_session, run_session, get_data_file, get_eeg_marks
from sibley.devices.default_eeg import DefaultEEG
from sibley.devices.epoc import EPOC
from sibley.devices.muse import Muse
from sibley.task.media import record_audio, show_text
from sibley.utils import windows_process_running, windows_taskkill, fix_muse_data, zip_folder



# using global variable (and not class-level) to circumvent library-related issues
# specifically, marker injection fails when with class-level variable
eeg_device = None


# using global to improve code readability (reduces "self hell")
params = None
data_file = None  # initialized by store_settings from session config['data_capture'], using captured data types



'''
params_default = {'study': 'unknown',
                'session_type': 'sibley_home_2209',
                'eeg_device': 'unknown',
                'participant_id': 'unknown',
                'group': 'unknown',
                'age': 'unknown',
                'comments': 'unknown',
                'session_uuid': 'unknown',
                'timestamp': 'unknown',
                'user_interface': 'muse'}
'''
#if a path exists to an input json, then read it and overwrite the default params to those
if os.path.exists(glob.glob('input\*.json')[0]):
    
    json_paths = glob.glob('input\*.json')

    with open(json_paths[0]) as param_json:
        params_default = json.load(param_json)
    
else:
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
    '''
    Init will run the tkinter GUI, which has three main step: 
    1) equipping the device. 
    2) connection and quality control -> 2.5) run psychopy session. 
    3) end program/save data. 
    Each window will be deleted by the "next" button, which will also control 
    a switch that enables progression to the next step.

    To connect the device:
    1. Gui_muse will create a muse class object called eeg_device
    2. eeg_device is assigned a Thread class
        a) this class has a parameter "target" which determines what gets run by this thread. the target is set to bluemuse_keeper. 
           the keeper, is a function inside muse.py that checks the connection and if it's dropped, it reconnects.
        b) the keeper repeats the following inside a while TRUE loop:
            0) nircmd supression of bluemuse and museLSL
            i) assign bluemuse_running by whether there is a windows process called BlueMuse.exe
            ii) start bluemuse if it's not running.
            iii) if it is running, then check the streaming status.
            iv) if not streaming, then start streaming
            v) if streaming just went from off to on, then use nircmd to supress LSL bridge (and we added BlueMuse supress)
            vi) wait 2 seconds.
    '''

    def __init__(self):

        global eeg_device
        global params

        eeg_device = None
        self.checkpoint_1 = False
        self.checkpoint_2 = False

        #make any necessary folders, if they don't already exist.
        self.task_log = []
        self.device = device_default
        self.session_duration, self.session_config_file = list_session()
        folders_required = ['session_media/audio', 'session_media/images', 'session_media/video'
                            'output/audio', 'output/info', 'output/keyboard', 'output/motion', 'output/session',
                            'session_logs', 'session_config']
        folders_required += ['output/EEG/' + item for item in list(self.device.values())]
        for item in folders_required:
            os.makedirs(item, exist_ok=True)

        params = params_default #TO-DO this can be loaded in from a JSON at some point. 
        

        if params['user_interface']=='muse':

            #create a screen to hold the first display window (shows how to equip device)
            self.root = Tk()
            self.root.geometry("1200x650")
            self.root.title("Sibley EEG v0.1")

            #create a muse class object
            eeg_device = Muse()

            #here we create a thread where the argument target is called when you run it.
            eeg_device.thread_bluemuse = Thread(target=eeg_device.bluemuse_keeper, daemon=True, name='Monitor')
            eeg_device.thread_bluemuse.start() # activate bluemuse_keeper.
            
            #this is where sibley displays the instructions on how to wear the device
            self.display_window_step01()

            #first checkpoint determines whether the "Next" button was clicked. If so, proceed to step 2, otherwise skip to the ending of the program.
            if self.checkpoint_1 == True:

                #create a screen to hold the second display window (shows connection and quality control status)
                self.root = Tk()
                self.root.geometry("1200x650")
                self.root.title("Sibley EEG v0.1")
                self.display_window_step02()

                #makes the streaming data discoverable
                eeg_device.open_outlet()
                self.store_settings()

                #second checkpoint determines whether the "start session" button was successfully clicked. 
                # If so, start session otherwise skip to the ending of the program.
                if self.checkpoint_2 == True:

                    #start session runs whatever neurocognitive test was selected.
                    self.start_session()
                    
                    #create a screen to hold the third display window (the closing window)
                    self.root = Tk()
                    self.root.geometry("1200x650")
                    self.root.title("Sibley EEG v0.1")
                    self.display_window_step03()

                    #save your data
                    self.save_session()
            
            # kills: BlueMuse AND eeg_device.process_bluemuse_stream. Then end the program using the Sys module which is always available
            eeg_device.bluemuse_exit() 
            sys.exit()

    def activate_switch(self):
        '''
        This is a function that is called when a "next" button is clicked. The logic gates determine which point of the program the user is at
        then set the checkpoint to true so that the user can progress. Without setting these checkpoints to true (i.e. clicking the close window button)
        you will skip to the end of the program and call sys.exit()
        '''
        #if you are between windows 1 and 2
        if (self.checkpoint_1 == False) and (self.checkpoint_2 ==False):
            self.checkpoint_1 = True
            self.root.destroy()
        #if you are trying to start the session
        elif (self.checkpoint_1 == True) and (self.checkpoint_2 ==False):
            self.checkpoint_1 = False
            self.checkpoint_2 = True
            self.root.destroy()
        #if you are neither of these, there must be a mistake
        else:
            assert False, 'Checkpoints are messed up'
            
    def store_settings(self):
        '''
        This is called right before the session begins. It sets the fields that are required when you want to later
        save your data. 
        '''
        global params
        global data_file
        
        
        #hard code some of the settings. TO-DO In the future, we want to make this more automated.  
        params['timestamp'] = time.strftime("%Y%m%d-%H%M%S")
        data_file = get_data_file('session_config/' + self.session_config_file[params['session_type']])

        #at the moment, we are not accepting audio and keyboard input from the user, but if we were
        #this is where it creates a name for those files
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
        '''
        Method for actually running whatever neurocognitive test you wanted to run. 
        '''
        global eeg_device
        global params
        global data_file
        print('################ starting the session ########################')
        print('with the params set to: ', params)

        #if you are going to collect audio, turn on the microphone.
        if 'audio' in data_file.keys():
            m, s = divmod(self.session_duration[params['session_type']], 60)
            record_audio(filename=data_file['audio'], until=str(m) + ':' + str(s))

        #if your device is either form of Muse, start recording the muse EEG data using muse.py
        if params['eeg_device'] == 'Muse 2' or params['eeg_device'] == 'Muse S':
            
            #define file name for the EEG data
            data_file['EEG'] = 'output/EEG/' + self.device[params['eeg_device']] + '/' + params['timestamp'] + '_' + params['study'] + '_' + params['participant_id'] + '.csv'
            #start recording data                   
            eeg_device.record_muse_data(fn=data_file['EEG'], duration=self.session_duration[params['session_type']])

        #start a psychopy window
        mywin = visual.Window(monitor="testMonitor", units="deg", fullscr=True, color=[-1, -1, -1])
        
        #run the session and assign any output to the task logs
        self.task_log = run_session(filename='session_config/' + self.session_config_file[params['session_type']], eeg=eeg_device, win=mywin, data_file=data_file)

        #when the session is done, show a screen of text saying they are done.
        show_text(win=mywin, text='Session completed:\n\n' + params['session_type'], duration=4)

        #close the psychopy window
        mywin.close()

    def save_session(self):
        global params
        global data_file
        print(data_file)
        
        #this creates a random serial code to associate with the session number.
        params['session_uuid'] = str(uuid.uuid4()) #TO-DO determine if this is necessary

        #assign a name for the output file as a composite of a few parameters. Create the path for that file.
        session_name = params['timestamp'] + '_' + params['study'] + '_' + params['participant_id']
        Path("output/session/" + session_name).mkdir(parents=True, exist_ok=True)

        #start a new dictionary where we will store data about this session run. 
        session = {'params': params, 'data_file': data_file}

        #if you want to collect EEG data (this is technically optional), then you will also need to collect the markings 
        #to timestamp the events during your neurocognitive testing.
        if 'EEG' in data_file.keys():
            if data_file['EEG'] != 'none':
                session['EEG_marks'] = get_eeg_marks('session_config/' + self.session_config_file[params['session_type']])

        #assign the output to this session
        session['task_log'] = self.task_log

        #write a JSON containing all the info about the session (EEG mark definitions, params, task log) to output/info
        with open('output/info/' + session_name + '.json', 'w') as outfile:
            json.dump(session, outfile, indent=4)
        shutil.copyfile('output/info/' + session_name + '.json', 'output/session/' + session_name + '/session_info.json')


        if 'EEG' in data_file.keys():
            if data_file['EEG'] == 'none':  # this is exe session supports EEG capture, but it was executed with "no EEG device"
                open('output/session/' + session_name + '/EEG_none.txt', mode='a').close()  # creates empty file
            else:
                if params['eeg_device'] == 'Muse 2' or params['eeg_device'] == 'Muse S':
                    fix_muse_data(data_file['EEG'])
                # data_file['EEG'] can contain one file (Muse) or multiple (EPOC)
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
            eeg_device.keep_alive_muse = False
            eeg_device.bluemuse_exit()
            if sys_exit:
                sys.exit()


    def dialog_about(self):
        mbox.showerror('About', 'Sibley EEG v0.1 (development version')

    def display_window_step01(self):
        '''
        This is function used to display an image that contains the instructions for putting on a muse headband.
        Includes buttons for:
        - about
        - exit
        - next (starts quality control)

        '''
        #these variables define a series of column (c) and row (r) coordinates to 
        #define various locations on the screen
        col_1 = 20 #presumably farthest left column
        col_2 = 220
        col_3 = 350
        col_4 = 820
        col_5 = 1085 #presumably farthest right column
        row_0 = 20 # top row
        row_1 = 100
        row_2 = 200
        row_3 = 300
        row_4 = 400
        row_5 = 500
        row_6 = 575 # bottom row
        
        #define font sizes
        config_font_large = ("Helvetica", 24)
        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)
        
        #define administrative about and exit buttons
        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=col_1, y=row_0)
        # 'Button(command=...)' does not allow args (this triggers the action without pressing the button)
        # 'partial(func, arg1, arg2, ...)' is a workaround; lambda functions can also be used
        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=partial(self.close_window, confirmation_prompt=True, sys_exit=True), state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=col_5 - 100, y=row_0)
        
        #display headband image and label with text
        self.label_step1 = Label(self.root, text="Step 1: prepare the headband", font=config_font_large).place(x=col_3, y=row_0)
        self.canvas = Canvas(self.root, width = 420, height = 400)
        self.canvas.place(x=0, y=row_2)
        headband_image_file = Image.open("session_media/images/muse_headband_install.jpg")
        headband_image = ImageTk.PhotoImage(headband_image_file)
        headband_image_label = Label(image=headband_image)
        headband_image_label.place(x=0, y=row_2)

        # create next-screen button and label it with "when read, press" 
        self.label_start_qc = Label(self.root, text="When ready, press ----- >", font=config_font).place(x=col_1, y=row_6)
        self.button_start_qc = Button(self.root, text="Next", font=config_font_medium, width=15,
                                           height=1, command=self.activate_switch, state=NORMAL, bg='green')
        self.button_start_qc.place(x=col_3, y=row_6)

        #tkinter function that makes the screen appear indefinitely
        self.root.mainloop()


    def display_window_step02(self):
        '''
        This is function used to display the status of the EEG (Muse) headband including the connection, battery level, and quality check which displays an image of a horseshoe diagram to represent the EEG sensors with adequate quality check.
        Includes buttons for:
        - about
        - exit
        - start (starts the session)

        '''
        global eeg_device
        
        #these variables define a series of column (c) and row (r) coordinates to 
        #define various locations on the screen
        col_1 = 20 #presumably farthest left column
        col_2 = 220
        col_3 = 350
        col_4 = 820
        col_5 = 1085 #presumably farthest right column
        row_0 = 20 # top row
        row_1 = 100
        row_2 = 200
        row_3 = 300
        row_4 = 400
        row_5 = 500
        row_6 = 575 # bottom row

        # define font and sizes
        config_font_large = ("Helvetica", 24)
        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)

        # define administrative about and exit buttons
        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=col_1, y=row_0)
        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=partial(self.close_window, confirmation_prompt=True, sys_exit=True), state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=col_5 - 100, y=row_0)

        # Display EEG (Muse) connection status and label with text, starting status is 'No connection', to be updated using update_
        self.label_muse_status = Label(self.root, text="Muse headband status:", font=config_font).place(x=col_1, y=row_2)
        self.label_muse_status_msg = Label(self.root, text="", font=config_font)
        self.label_muse_status_msg.place(x=col_3, y=row_2)
        self.label_muse_status_msg.config(text='No connection', fg='red')

        # Display EEG (Muse) battery level and label with text, starting status is '- - -'
        self.label_muse_battery = Label(self.root, text="Muse headband battery:", font=config_font).place(x=col_1, y=row_3)
        self.label_muse_battery_msg = Label(self.root, text="", font=config_font)
        self.label_muse_battery_msg.place(x=col_3, y=row_3)
        self.label_muse_battery_msg.config(text='- - -', fg='black')

        # Display EEG Quality Check status and label with text, starting status is '- - -'
        self.label_eeg_qc = Label(self.root, text="EEG quality check:", font=config_font).place(x=col_1, y=row_4)
        self.label_eeg_qc_msg = Label(self.root, text="", font=config_font)
        self.label_eeg_qc_msg.place(x=col_3, y=row_4)
        self.label_eeg_qc_msg.config(text='- - -', fg='black')

        # create next-screen button and label it with "Start session" to start the session, once the button is pressed the command will close the window
        self.label_start_session = Label(self.root, text="Session", font=config_font).place(x=col_1, y=row_6)
        self.button_start_session = Button(self.root, text="Start session", font=config_font_medium, width=15,
                                           height=1,
                                           command=self.activate_switch, state=DISABLED, bg='grey')
        self.button_start_session.place(x=col_3, y=row_6)

        #display rectangle using Canvas and label with text
        self.label_step1 = Label(self.root, text="Step 2: establish data link", font=config_font_large).place(x=col_3, y=row_0)
        self.canvas = Canvas(self.root, width = 420, height = 400)
        self.canvas.create_rectangle(2, 10, 380, 380)
        self.canvas.place(x=720, y=150)

        # Display the initial null quality check (all grey) horsehoe for Muse EEG headband.
        # Image.open (from PIL) handles more image formats than the default PhotoImage (can open certain types directly)
        #self.image1_pre = Image.open("session_media/images/horseshoe_n_n_n_n.png")
        #self.image1 = ImageTk.PhotoImage(self.image1_pre)
        #self.label_horseshoe = Label(image=self.image1)
        #self.label_horseshoe.place(x=800, y=250)

        # New horseshoe and individual electrode correspondence here
        self.image2_pre = Image.open("session_media/images/horseshoe_all.png")
        self.image2 = ImageTk.PhotoImage(self.image2_pre)
        self.label2_horseshoe = Label(image=self.image2)
        self.label2_horseshoe.place(x=800, y=250)
        #  Electrode 1
        self.image_electrode1_pre = Image.open("session_media/images/electrode_null.png")
        self.image_electrode1 = ImageTk.PhotoImage(self.image_electrode1_pre)
        self.label_electrode1 = Label(image=self.image_electrode1)
        self.label_electrode1.place(x=col_4, y=row_4-20)
        #  Electrode 2
        self.image_electrode2_pre = Image.open("session_media/images/electrode_null.png")
        self.image_electrode2 = ImageTk.PhotoImage(self.image_electrode2_pre)
        self.label_electrode2 = Label(image=self.image_electrode2)
        self.label_electrode2.place(x=col_4+20, y=row_3-30)
        #  Electrode 3
        self.image_electrode3_pre = Image.open("session_media/images/electrode_null.png")
        self.image_electrode3 = ImageTk.PhotoImage(self.image_electrode3_pre)
        self.label_electrode3 = Label(image=self.image_electrode3)
        self.label_electrode3.place(x=col_4+100, y=row_3-30)
        #  Electrode 4
        self.image_electrode4_pre = Image.open("session_media/images/electrode_null.png")
        self.image_electrode4 = ImageTk.PhotoImage(self.image_electrode4_pre)
        self.label_electrode4 = Label(image=self.image_electrode4)
        self.label_electrode4.place(x=col_4+125, y=row_4-20)
        

        # Display Muse headband image and label with text, starting status is '- - -'
        self.label_horseshoe = Label(self.root, text="EEG sensor status", font=config_font).place(x=col_4-35, y=row_2)
        self.label_horseshoe_msg = Label(self.root, text="", font=config_font)
        self.label_horseshoe_msg.place(x=col_4-60, y=row_5-40)
        self.label_horseshoe_msg.config(text ='                    - - -        ', fg='black', font=config_font_medium)


        # Tkinter function to move a window up of the stack, this is the window stacking order
        self.root.lift()
        #self.root.attributes('-topmost', True)
        #self.root.after_idle(self.root.attributes, '-topmost', False)

        # Tkinter function to schedule an action (update_gui_muse) after a time has elapsed, 1000ms = 1s
        self.root.after(1000, self.update_gui_muse())
        
        #tkinter function that makes the screen appear indefinitely
        self.root.mainloop()


    def update_gui_muse(self):
        print('update_gui_muse (for horseshoe update)')
        global eeg_device
        
        col_4 = 820 # TO-DO: cleanup make col & row global for the module!
        row_3 = 300
        row_4 = 400

        eeg_device.update_status_telemetry()

        print('bluemuse running:' , eeg_device.status['bluemuse_running'],
            'device is connected to bluemuse: ', eeg_device.status['is_connected' ],
            'device streaming: ',eeg_device.status['is_streaming'], 
            'channel quality summary: ', eeg_device.status['channel_summary'], '\n')
        
        
        if eeg_device.status['is_connected']==True:
            self.label_muse_status_msg.config(text="Connected", fg='green')
            self.label_muse_battery_msg.config(text=str(eeg_device.status['battery_level']), fg='green')

            eeg_device.update_status_channel_qc()

            #self.image1_pre = Image.open('session_media/images/horseshoe_' + eeg_device.status['channel_summary'] + '.png')
            #self.image1 = ImageTk.PhotoImage(self.image1_pre)
            #self.label_horseshoe = Label(image=self.image1)
            #self.label_horseshoe.place(x=800, y=250)
            
            #  Electrode 1
            if eeg_device.status['channel_summary'][0] == 'g':
                self.image_electrode1_pre = Image.open("session_media/images/electrode_green.png")
                #self.image_electrode1 = ImageTk.PhotoImage(self.image_electrode1_pre)
                #self.label_electrode1 = Label(image=self.image_electrode1)
                #self.label_electrode1.place(x=col_4, y=row_4-20)
            else:
                self.image_electrode1_pre = Image.open("session_media/images/electrode_red.png")
            self.image_electrode1 = ImageTk.PhotoImage(self.image_electrode1_pre)
            self.label_electrode1 = Label(image=self.image_electrode1)
            self.label_electrode1.place(x=col_4, y=row_4-20)
            #  Electrode 2
            if eeg_device.status['channel_summary'][2] == 'g':
                self.image_electrode2_pre = Image.open("session_media/images/electrode_green.png")
            else:
                self.image_electrode2_pre = Image.open("session_media/images/electrode_red.png")
            self.image_electrode2 = ImageTk.PhotoImage(self.image_electrode2_pre)
            self.label_electrode2 = Label(image=self.image_electrode2)
            self.label_electrode2.place(x=col_4+20, y=row_3-30)
            #  Electrode 3
            if eeg_device.status['channel_summary'][4] == 'g':
                self.image_electrode3_pre = Image.open("session_media/images/electrode_green.png")
            else:
                self.image_electrode3_pre = Image.open("session_media/images/electrode_red.png")
            self.image_electrode3 = ImageTk.PhotoImage(self.image_electrode3_pre)
            self.label_electrode3 = Label(image=self.image_electrode3)
            self.label_electrode3.place(x=col_4+100, y=row_3-30)
            #  Electrode 4
            if eeg_device.status['channel_summary'][6] == 'g':
                self.image_electrode4_pre = Image.open("session_media/images/electrode_green.png")
            else:
                self.image_electrode4_pre = Image.open("session_media/images/electrode_red.png")
            self.image_electrode4 = ImageTk.PhotoImage(self.image_electrode4_pre)
            self.label_electrode4 = Label(image=self.image_electrode4)
            self.label_electrode4.place(x=col_4+125, y=row_4-20)
            
            if eeg_device.status['channel_summary'] == 'g_g_g_g':
                self.label_eeg_qc_msg.config(text='Pass', fg='green')
                self.label_horseshoe_msg.config(text='          Good signal              ', fg='green')
                self.button_start_session.config(state=NORMAL, bg='green')
            else:
                self.label_eeg_qc_msg.config(text='Fail', fg='red')
                self.label_horseshoe_msg.config(text='         Adjust headband          ', fg='red')
                self.button_start_session.config(state=NORMAL, bg='grey')

        self.root.after(1000, self.update_gui_muse)

    def display_window_step03(self):

        '''
        This is function used to display the ending status of the EEG (Muse) headband including which displays an image of the headband.
        Includes buttons for:
        - about
        - exit
        - close program (close the window)

        '''

        #these variables define a series of column (c) and row (r) coordinates to 
        #define various locations on the screen
        col_1 = 20 #presumably farthest left column
        col_2 = 220
        col_3 = 350
        col_4 = 820
        col_5 = 1085 #presumably farthest right column
        row_0 = 20 # top row
        row_1 = 100
        row_2 = 200
        row_3 = 300
        row_4 = 400
        row_5 = 500
        row_6 = 575 # bottom row

        # define font and sizes
        config_font_large = ("Helvetica", 24)
        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)

        #define administrative about and exit buttons
        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=col_1, y=row_0)
        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=partial(self.close_window, confirmation_prompt=False, sys_exit=True), state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=col_5 - 100, y=row_0)

        # Display headband ending image and label with text
        self.label_step1 = Label(self.root, text="Step 3: session complete", font=config_font_large).place(x=col_3, y=row_0)
        self.canvas = Canvas(self.root, width = 420, height = 400)
        self.canvas.place(x=0, y=row_2)
        headband_end_image_file = Image.open("session_media/images/muse_headband_end_ok.jpg")
        headband_end_image = ImageTk.PhotoImage(headband_end_image_file)
        label1 = Label(image=headband_end_image)
        label1.place(x=col_2-70, y=row_2)

        # create next-screen button and label it with "Close program", once the button is pressed the command will close the window
        #self.label_start_session = Label(self.root, text="When ready, press ----- >", font=config_font).place(x=col_1, y=row_6)
        self.please_wait_label = Label(self.root, text="Please wait 10 seconds then click button below", font=config_font_large).place(x=col_3, y=row_5)
        self.button_end_session = Button(self.root, text="Close program", font=config_font_medium, width=15, height=1,
                                           command=partial(self.close_window, confirmation_prompt=False, sys_exit=False), state=NORMAL, bg='green')
        self.button_end_session.place(x=col_3, y=row_6)
        
        self.root.mainloop()
        # Tkinter function that makes the screen appear indefinitely
        
        #time.sleep(10)
        #self.button_start_session = Button(self.root, text="Close program", font=config_font_medium, width=15, height=1,
         #                                  command=partial(self.close_window, confirmation_prompt=False, sys_exit=False), state=NORMAL, bg='green')
        #self.button_start_session.place(x=col_3, y=row_6)
        #self.root.mainloop()

