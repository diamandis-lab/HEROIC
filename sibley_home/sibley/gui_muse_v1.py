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
from sibley.utils import zip_folder
import json
from PIL import ImageTk,Image

# using global variable (and not class-level) to circumvent library-related issues
# specifically, marker injection fails when with class-level variable
eeg_device = None

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


        global eeg_device
        eeg_device = DefaultEEG()
        global params
        params = params_default
        self.task_log = []
        self.device = device_default
        self.session_duration, self.session_config_file = list_session()
        self.study = {'default': 0}  # drop-down menu options, to be developed
        self.group = {'default': 0}  # drop-down menu options, to be developed
        folders_required = ['session_media/audio', 'session_media/images', 'session_media/video'
                            'output/audio', 'output/info', 'output/keyboard', 'output/motion', 'output/session',
                            'session_logs', 'session_config']
        folders_required += ['output/EEG/' + item for item in list(self.device.values())]
        for item in folders_required:
            os.makedirs(item, exist_ok=True)

        params['user_interface'] = 'muse'

        if params['user_interface']=='laboratory':
            self.root = Tk()
            self.root.geometry("1200x650")
            self.root.title("Sibley EEG v0.1")
            self.display_window()
        if params['user_interface']=='muse':

            params['study'] = 'unknown'
            params['session_type'] = 'stroop_keyboard'
            params['eeg_device'] = 'Muse 2'

            eeg_device = Muse()
            eeg_device.open_bluemuse()

            self.root = Tk()
            self.root.geometry("1200x650")
            self.root.title("Sibley EEG v0.1")
            self.display_window_step01()



            self.root = Tk()
            self.root.geometry("1200x650")
            self.root.title("Sibley EEG v0.1")
            self.launch_eeg()
            self.display_window_step02()


    def close_window(self):
        exit_program = True
        if params['session_uuid'] == 'unknown':
            result = mbox.askquestion("Exit application",
                                      "Do you want to close the program without saving the results?",
                                      icon='warning')
            if result == 'no':
                exit_program = False
        if exit_program:
            if windows_process_running('BlueMuse.exe'):
                windows_taskkill('BlueMuse.exe')
            if windows_process_running("EmotivPro.exe"):
                windows_taskkill('EmotivPro.exe')
            self.root.destroy()

    def reset_info(self):
        global params
        global data_file
        params = params_default
        data_file = None
        self.dropdown_study.config(state=DISABLED)
        self.dropdown_study.set(get_dict_keys(self.study)[0])
        self.dropdown_session_type.config(state="readonly")
        self.dropdown_session_type.set(get_dict_keys(self.session_duration)[0])
        self.dropdown_device.config(state="readonly")
        self.dropdown_device.set(get_dict_keys(self.device)[0])
        self.textfield_participant_id.config(state=NORMAL, bg='white')
        self.textfield_participant_id.delete(1.0, END)
        self.dropdown_group.config(state=DISABLED)
        self.dropdown_group.set(get_dict_keys(self.group)[0])
        self.textfield_age.config(state=NORMAL, bg='white')
        self.textfield_age.delete(1.0, END)
        self.button_store_settings.config(state=NORMAL)
        self.button_launch_eeg.config(state=DISABLED)
        self.button_start_session.config(state=DISABLED)
        self.button_load_edf.config(state=DISABLED)
        self.button_load_motion.config(state=DISABLED)
        self.button_save_session.config(state=DISABLED)
        self.label_store_settings.config(text='')
        self.label_launch_eeg.config(text='')
        self.label_start_session.config(text='')
        self.label_load_edf.config(text='')
        self.label_load_motion.config(text='')
        self.label_save_session.config(text='')
        self.textfield_comments.config(state=NORMAL, bg='white')

    def dialog_about(self):
        mbox.showerror('About', 'Sibley EEG v0.1 (development version')

    def store_settings(self):
        global params
        global data_file
        self.label_store_settings.config(text='\u2713', fg='green')
        params['study'] = self.dropdown_study.get()
        params['session_type'] = self.dropdown_session_type.get()
        data_file = get_data_file('session_config/' + self.session_config_file[params['session_type']])
        params['eeg_device'] = self.dropdown_device.get()
        participant_id = self.textfield_participant_id.get('1.0', END)[:-1]
        params['participant_id'] = participant_id.replace(' ', '-')
        params['group'] = self.dropdown_group.get()
        params['age'] = self.textfield_age.get("1.0", END)[:-1]
        params['timestamp'] = time.strftime("%Y%m%d-%H%M%S")
        self.dropdown_study.config(state=DISABLED)
        self.dropdown_session_type.config(state=DISABLED)
        self.dropdown_device.config(state=DISABLED)
        self.textfield_participant_id.config(state=DISABLED, bg='grey90')
        self.dropdown_group.config(state=DISABLED)
        self.textfield_age.config(state=DISABLED, bg='grey90')
        self.button_store_settings.config(state=DISABLED)
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
        if 'motion' not in data_file.keys():
            self.label_load_motion.config(text='\u2717', fg='red')
        if params['eeg_device'] == 'Muse 2' or params['eeg_device'] == 'Muse S':
            self.label_load_edf.config(text='\u2717', fg='red')
            self.button_launch_eeg.config(state=NORMAL)
        if params['eeg_device'] == 'EPOC X':
            self.button_launch_eeg.config(state=NORMAL)
        if self.device[params['eeg_device']] == 'none':
            self.label_launch_eeg.config(text='\u2717', fg='red')
            self.label_load_edf.config(text='\u2717', fg='red')
            self.button_start_session.config(state=NORMAL)

    def launch_eeg(self):
        global eeg_device
        global params
        print(eeg_device.info)
        print(eeg_device.status)

        move_on = False
        if params['eeg_device'] == 'Muse 2' or params['eeg_device'] == 'Muse S':
            eeg_device = Muse()
            eeg_device.open_stream()  # handled by muselsl
            #streams = resolve_byprop('type', 'EEG', timeout=10)  # pylsl
            #eeg_device.stream
            streams_eeg = resolve_byprop('type', 'EEG', timeout=10)
            #streams_telemetry = resolve_byprop('type', 'telemetry', timeout=10)
            if len(streams_eeg) > 0:
                eeg_device.status['is_connected'] = True

            #if eeg_device.status['is_connected']:
            #if len(eeg_device.stream) > 0:
            #    print(eeg_device.status)

                #eeg_device.view()  # stream returns is_stream_open
                # the 'muselsl view' window has to be close manually for now
                # Muse EEG session starts in 'start_session' so that the EEG data capture starts with session launch
                move_on = True
            else:
                mbox.showerror('Python Error Message', 'Error: Muse stream not found. Is the device on?')
                move_on = False

        if params['eeg_device'] == 'EPOC X':
            eeg_device = EPOC()
            move_on = True

        if move_on:
            eeg_device.open_outlet()  # applies to both EPOC and Muse
            if params['user_interface']=='laboratory':
                self.button_launch_eeg.config(state=DISABLED)
                self.label_launch_eeg.config(text='\u2713', fg='green')
                self.button_start_session.config(state=NORMAL)

    def start_session(self):
        global eeg_device
        global params
        global data_file
        print('start_session')
        self.button_start_session.config(state=DISABLED)
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
        self.label_start_session.config(text='\u2713', fg='green')

        if params['eeg_device'] == 'EPOC X':
            self.button_load_edf.config(state=NORMAL)
        else:
            if 'motion' in data_file.keys():
                self.button_load_motion.config(state=NORMAL)
            else:
                self.button_save_session.config(state=NORMAL)

    def load_edf(self):
        global params
        global data_file
        files_all = os.listdir('output/EEG/EPOCX')
        files_md_edf = ['output/EEG/EPOCX/' + v for v in files_all if '.md.edf' in v]
        for filename in files_md_edf:
            os.rename(filename, filename.replace('.md.edf', '.mdedf'))
        files_interval_marker = ['output/EEG/EPOCX/' + v for v in files_all if '_intervalMarker' in v]
        for filename in files_interval_marker:
            os.rename(filename, filename.replace('_intervalMarker.csv', '.csv'))
        file_selected = askopenfilename(initialdir=os.getcwd() + "\\output\\EEG\\EPOCX",
                                        title="Select file",
                                        filetypes=(("EDF files", "*.edf"), ("all files", "*.*")))
        if file_selected:
            files_all = os.listdir('output/EEG/EPOCX')
            print('files_all:')
            print(files_all)
            filename, file_extension = os.path.splitext(os.path.basename(file_selected))  # file_selected is full path
            files_session = ['output/EEG/EPOCX/' + v for v in files_all if filename in v]
            print('files_session: ')
            print(files_session)
            data_file['EEG'] = '|'.join(files_session)
            print(data_file['EEG'])
            self.label_load_edf.config(text='\u2713', fg='green')
            self.button_load_edf.config(state=DISABLED)
            if 'motion' in data_file.keys():
                self.button_load_motion.config(state=NORMAL)
            else:
                self.button_save_session.config(state=NORMAL)
        else:
            mbox.showerror('Error Message', 'A valid EDF file must be selected!')

    def load_motion(self):
        global params
        global data_file
        file_selected = askopenfilename(initialdir=os.getcwd() + '\\output\\motion',
                                        title="Select file",
                                        filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
        if file_selected:
            data_file['motion'] = file_selected
            self.label_load_motion.config(text='\u2713', fg='green')
            self.button_load_motion.config(state=DISABLED)
            self.button_save_session.config(state=NORMAL)
        else:
            mbox.showerror('Error Message', 'A valid EDF file must be selected!')

    def save_session(self):
        global params
        global data_file
        print(data_file)
        params['comments'] = self.textfield_comments.get("1.0", END)[:-1]
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
        if 'motion' in data_file.keys():
            filename, file_extension = os.path.splitext(os.path.basename(data_file['motion']))
            shutil.copyfile(data_file['motion'], 'output/session/' + session_name + '/motion' + file_extension)

        zip_folder(dir_home=os.getcwd() + '\\output',
                   dir_parent=os.getcwd() + '\\output\\session\\',
                   dir_target=session_name,
                   file_extension='sbl')
        shutil.rmtree(os.getcwd() + '\\session\\' + session_name)

        self.button_save_session.config(state=DISABLED)
        self.label_save_session.config(text='\u2713', fg='green')
        self.textfield_comments.config(state=DISABLED, bg='grey90')
        print('saving session...')
        os.chdir('../') #  restores base directory, it got switched to output/
        print(os.getcwd())

    def display_window(self):

        c1 = 20
        c2 = 220
        c3 = 620
        c4 = 820
        c5 = 1085
        r0 = 20
        r1 = 100
        r2 = 175
        r3 = 250
        r4 = 325
        r5 = 375
        r6 = 425
        r7 = 475
        r8 = 525
        r9 = 575

        config_font = ("Helvetica", 20)
        config_font_medium = ("Helvetica", 16)
        config_font_small = ("Helvetica", 12)

        self.button_about = Button(self.root, text="About", font=config_font_small, width=15, height=1,
                                   command=self.dialog_about, state=NORMAL, bg='khaki')
        self.button_about.place(x=c1, y=r0)
        self.button_reset = Button(self.root, text="Reset", font=config_font_small, width=15, height=1,
                                   command=self.reset_info, state=NORMAL, bg='yellow')
        self.button_reset.place(x=c5 - 280, y=r0)
        self.button_exit = Button(self.root, text="Exit", font=config_font_small, width=15, height=1,
                                  command=self.close_window, state=NORMAL, bg='deep sky blue')
        self.button_exit.place(x=c5 - 100, y=r0)

        self.label_study = Label(self.root, text="Study",
                                 font=config_font).place(x=c1, y=r1)
        self.dropdown_study = ttk.Combobox(self.root, state=DISABLED, font=config_font,
                                           values=get_dict_keys(self.study))
        self.dropdown_study.set(get_dict_keys(self.study)[0])
        self.dropdown_study.place(x=c2, y=r1)

        self.label_session_type = Label(self.root, text="Session type",
                                        font=config_font).place(x=c1, y=r2)
        self.dropdown_session_type = ttk.Combobox(self.root, state="readonly",
                                                  values=get_dict_keys(self.session_duration),
                                                  font=config_font)
        self.dropdown_session_type.set(get_dict_keys(self.session_duration)[0])
        self.dropdown_session_type.place(x=c2, y=r2)
        self.label_device = Label(self.root, text="EEG device",
                                  font=config_font).place(x=c1, y=r3)
        self.dropdown_device = ttk.Combobox(self.root, state="readonly",
                                            values=get_dict_keys(self.device),
                                            font=config_font)
        self.dropdown_device.set(get_dict_keys(self.device)[0])
        self.dropdown_device.place(x=c2, y=r3)
        self.label_participant_id = Label(self.root, text="Participant ID",
                                          font=config_font).place(x=c3, y=r1)
        self.textfield_participant_id = Text(self.root, width=21, height=1,
                                             font=config_font)
        self.textfield_participant_id.place(x=c4, y=r1)
        self.label_group = Label(self.root, text="Group",
                                 font=config_font).place(x=c3, y=r2)
        self.dropdown_group = ttk.Combobox(self.root, state=DISABLED,
                                           values=get_dict_keys(self.group),
                                           font=config_font)
        self.dropdown_group.set(get_dict_keys(self.group)[0])
        self.dropdown_group.place(x=c4, y=r2)
        self.label_age = Label(self.root, text="Age",
                               font=config_font).place(x=c3, y=r3)
        self.textfield_age = Text(self.root, width=21, height=1,
                                  font=config_font)
        self.textfield_age.place(x=c4, y=r3)
        self.separator2 = ttk.Separator(self.root, orient='horizontal')
        self.separator2.place(relx=0, y=r3 + 50, relwidth=1, relheight=1)
        self.label_store_settings = Label(self.root, text="", font=config_font)
        self.label_store_settings.place(x=c4 - 50, y=r4 + 10)
        self.button_store_settings = Button(self.root, text="Store settings", font=config_font_medium, width=15,
                                            height=1,
                                            command=self.store_settings, state=NORMAL)
        self.button_store_settings.place(x=c4, y=r4)

        self.label_launch_eeg = Label(self.root, text="", font=config_font)
        self.label_launch_eeg.place(x=c4 - 50, y=r5 + 10)
        self.button_launch_eeg = Button(self.root, text="Launch EEG app", font=config_font_medium, width=15,
                                        height=1,
                                        command=self.launch_eeg, state=DISABLED)
        self.button_launch_eeg.place(x=c4, y=r5)

        self.label_start_session = Label(self.root, text="", font=config_font)
        self.label_start_session.place(x=c4 - 50, y=r6 + 10)
        self.button_start_session = Button(self.root, text="Start session", font=config_font_medium, width=15,
                                           height=1,
                                           command=self.start_session, state=DISABLED)
        self.button_start_session.place(x=c4, y=r6)
        self.label_load_edf = Label(self.root, text="", font=config_font)
        self.label_load_edf.place(x=c4 - 50, y=r7 + 10)
        self.button_load_edf = Button(self.root, text="Load EDF", font=config_font_medium, width=15, height=1,
                                      command=self.load_edf, state=DISABLED)
        self.button_load_edf.place(x=c4, y=r7)

        self.label_load_motion = Label(self.root, text="", font=config_font)
        self.label_load_motion.place(x=c4 - 50, y=r8 + 10)
        self.button_load_motion = Button(self.root, text="Load motion", font=config_font_medium, width=15,
                                         height=1,
                                         command=self.load_motion, state=DISABLED)
        self.button_load_motion.place(x=c4, y=r8)
        self.label_save_session = Label(self.root, text="", font=config_font)
        self.label_save_session.place(x=c4 - 50, y=r9 + 10)
        self.button_save_session = Button(self.root, text="Save session", font=config_font_medium, width=15,
                                          height=1,
                                          command=self.save_session, state=DISABLED)
        self.button_save_session.place(x=c4, y=r9)

        self.label_comments = Label(self.root, text="Comments", font=config_font_medium)
        self.label_comments.place(x=c2, y=r4 + 10)
        self.textfield_comments = Text(self.root, width=64, height=11,
                                       font=config_font_small)
        self.textfield_comments.place(x=c1, y=r5)
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.after(1000, self.update_gui)
        self.root.mainloop()


    def display_window_step02(self):

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
                                  command=self.close_window, state=NORMAL, bg='deep sky blue')
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
                                           command=self.start_session, state=DISABLED, bg='grey')
        self.button_start_session.place(x=c3, y=r9)

        self.label_step1 = Label(self.root, text="Step 2: establish data link", font=config_font_large).place(x=c3, y=r0)

        self.canvas = Canvas(self.root, width = 420, height = 400)

        #self.canvas.create_line(300, r2, 900, r2)


        #self.canvas.create_line(2, 10, 2, 400)
        self.canvas.create_rectangle(2, 10, 380, 380)
        self.canvas.place(x=720, y=150)

        # Image.open (from PIL) handles more image formats than the default PhotoImage (can open certain types directly)
        self.image1_pre = Image.open("session_media/images/horseshoe_n_n_n_n.png")
        self.image1 = ImageTk.PhotoImage(self.image1_pre)
        self.label_horseshoe = Label(image=self.image1)
        self.label_horseshoe.place(x=800, y=250)

        self.label_eeg_qc = Label(self.root, text="EEG sensor status", font=config_font).place(x=c4-35, y=r2)
        self.label_eeg_qc_msg = Label(self.root, text="", font=config_font)
        self.label_eeg_qc_msg.place(x=c4-60, y=r5-40)
        #self.label_eeg_qc_msg.config(text='4 sensors are capturing good data', fg='green', font=config_font_medium)
        self.label_eeg_qc_msg.config(text ='                    - - -        ', fg='black', font=config_font_medium)
        self.root.after(1000, self.update_gui_muse)
        self.root.mainloop()

    def update_gui(self):
        global eeg_device
        eeg_device.update_status()
        self.root.after(1000, self.update_gui)

    def update_gui_muse(self):
        global eeg_device
        eeg_device.update_status()
        self.label_muse_status_msg.config(text=eeg_device.status['is_connected'], fg='black')
        self.label_muse_battery_msg.config(text=eeg_device.status['battery_level'], fg='black')
        self.root.after(1000, self.update_gui_muse)

        #image1 = Image.open('session_media/images/horseshoe_' + eeg_device.status['quality_summary'] +'.png')
        #test = ImageTk.PhotoImage(image1)
        #label1 = Label(image=test)
        #label1.place(x=800, y=250)
        self.image2_pre = Image.open("session_media/images/horseshoe_g_g_g_g.png")
        self.image2 = ImageTk.PhotoImage(self.image2_pre)

        self.label_horseshoe.configure(image=self.image2)
        self.label_horseshoe.image = self.image2

        #self.image2 = ImageTk.PhotoImage(image2_pre)
        #self.label_horseshoe = Label(image=image1)
        #self.label_horseshoe.place(x=800, y=250)
        #self.image2 = PhotoImage(file=path)
        #self.label.configure(image=self.image2)

    def display_window_step01(self):

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
                                  command=self.close_window, state=NORMAL, bg='deep sky blue')
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





