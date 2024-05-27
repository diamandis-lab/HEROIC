import subprocess
import os
import time
from multiprocessing import Process
#from threading import Thread
import pandas as pd
import numpy as np
from statistics import median

from mne.time_frequency import psd_multitaper
from mne.channels import make_standard_montage
from mne.io import RawArray
from mne import create_info

from muselsl import record
from pylsl import resolve_byprop, StreamOutlet, StreamInfo, stream_inlet

from sibley.utils import windows_process_running, windows_taskkill


class Muse:
    """Muse 2 or Muse X headband, interface by the muselsl library"""
    def __init__(self):
        self.keep_alive_muse = True

        self.outlet = None

        # background process that is launched by gui_muse, it executes the fuction 'bluemuse_keeper' recurrently
        self.process_bluemuse = None
        self.thread_bluemuse = None

        self.stream_telemetry = None
        self.inlet_telemetry = None
        self.stream_PPG = None
        self.inlet_PPG = None
        self.stream_eeg = None
        self.inlet_eeg = None
        self.info = {'device': 'muse'}
        self.status = {'is_connected': False,
                       'bluemuse_running': False,
                       'is_streaming': False,
                       'battery_level': None,
                       'quality_ch1': None,
                       'quality_ch2': None,
                       'quality_ch3': None,
                       'quality_ch4': None,
                       'channel_summary': 'n_n_n_n',
                       'ready': False}


    def start_bluemuse(self):
        '''
        This method will start the BlueMuse operations, refresh the Bluetooth list, then hides the BlueMuse window.
        '''
        print("muse.start_bluemuse()")
        # the first command will launch Bluemuse and modify settings (if needed)
        # it seems like Bluemuse stores settings from previous session; we re-do just in case
        cmd = 'start bluemuse:'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://refresh'
        subprocess.call(cmd, shell=True)
        time.sleep(1)
        # The window BlueMuse is minimized immediately to avoid causing confusion to the user
        os.system("C:\\PROGRA~1\\nircmd-x64\\nircmd.exe win hide title \"BlueMuse\"")


    def stream_open(self):
        '''
        This method runs the command line interface settings for BlueMuse.
        '''
        cmd = 'start bluemuse://refresh'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=eeg_enabled!value=true'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=ppg_enabled!value=true'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=gyroscope_enabled!value=false'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=accelerometer_enabled!value=false'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=telemetry_enabled!value=true'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://start?streamfirst=true'
        subprocess.call(cmd, shell=True)


    def bluemuse_keeper(self):
        '''
        This method keeps the connection between BlueMuse and the Muse device, and occurs periodically.
        '''
        while True:
            #  Uses nicrmd to supress the BlueMuse and LSL Bridge pop up windows.
            os.system("C:\\PROGRA~1\\nircmd-x64\\nircmd.exe win hide title \"BlueMuse\"")
            os.system("C:\\PROGRA~1\\nircmd-x64\\nircmd.exe win hide title \"LSL Bridge\"")
            
            # Built-in kill switch for this while true loop. 
            if self.keep_alive_muse==False:
                print('########### stopping bluemuse_keeper...')
                break

            # Determine if Bluemuse is running. print a couple variables.
            self.status['bluemuse_running'] = windows_process_running('BlueMuse.exe')
            
            # When BlueMuse is not running, then start running
            if self.status['bluemuse_running']==False:
                self.start_bluemuse()

            else:
                # Stores the fact that bluemuse is streaming
                is_streaming_old = self.status['is_streaming']
                # Get a new streaming update
                self.update_status_stream()

                # If not already streaming, then open a stream. this may be how sibley recovers dropped connections.
                if self.status['is_streaming']==False:
                    self.stream_open()

                #if the streaming status went from false to true, that means the BlueMuse gui will pop up
                # and so we need to supress the LSL bridge to prevent confusion. 
                if self.status['is_streaming'] == True and is_streaming_old == False:
                    # close the window titled "LSL Bridge" to avoid causing confusion to the user
                    os.system("C:\\PROGRA~1\\nircmd-x64\\nircmd.exe win hide title \"LSL Bridge\"")
                    #os.system("C:\\PROGRA~1\\nircmd-x64\\nircmd.exe win hide title \"BlueMuse\"")

            # Wait some time before running the loop again, every 2 seconds
            time.sleep(2)


    def bluemuse_exit(self):
        '''
        This method will close the BlueMuse stream and program window.
        '''
        #if self.process_bluemuse_stream.is_alive():
        #    self.process_bluemuse_stream.kill()
        if windows_process_running('BlueMuse.exe'):
            windows_taskkill('BlueMuse.exe')


    def update_status_stream(self):
        '''
        This method will update the status if the Muse device is streaming based on a pulled segment of data.
        '''
        # IMPORTANT: pull_sample(timeout=0) avoids blocking the execution
        # using Muse's PPG stream to check whether the device is streaming
        # when there is no new data, and empty array is returned (None, None)
        # if new information came through the channel: ...

        # without Muse, and empty stream is created, but not an inlet
        # eventually, when a data-containing stream is found, the inlet is initialized
        if self.inlet_PPG==None:
            self.stream_PPG = resolve_byprop('type', 'PPG', timeout=1)
            if len(self.stream_PPG)==1:
                self.inlet_PPG = stream_inlet(self.stream_PPG[0])

        if self.inlet_PPG!=None:
            data = self.inlet_PPG.pull_chunk()  # empty the buffer
            time.sleep(0.1)                     # wait 0.1s to refill
            PPG_sample = self.inlet_PPG.pull_sample(timeout=0) # sample the buffer, non-blocking in case streaming is down
            # Determines if there is data in the sample, then the status is streaming.
            if PPG_sample[0] != None:
                self.status['is_streaming'] = True
            else:
                self.status['is_streaming'] = False


    def update_status_telemetry(self):
        '''
        This is a function called every 1000ms by update gui muse. The purpose is to check the connected status
        and the battery level. Here's how it executes:
        1. creates a telemetry stream which is how you can get attributes of the device, not data.
        2. if this is the first time, set up inlet if you found a stream. 
        3. Every 10 seconds, once there is new data, they will do an update of the battery
        4. once a device is connected, it will say connected regardless of any changes to that.
        '''
        # IMPORTANT: pull_sample(timeout=0) avoids blocking the execution
        # telemetry has low frequency, ~0.1 Hz
        # when there is no new data, and empty array is returned (None, None)
        # if new information came through the channel: ([35.0, 3126.199951171875, 0.0, 0.0], 1637869946.443)
        print('update_status_telemetry (determines if connection exists)')

        # without Muse, an empty stream is created, but not an inlet
        # eventually, when a data-containing stream is found, the inlet is initialized
        if self.inlet_telemetry==None:
            self.stream_telemetry = resolve_byprop('type', 'Telemetry', timeout=1)
            if len(self.stream_telemetry)==1:
                self.inlet_telemetry = stream_inlet(self.stream_telemetry[0])

        else:
            telemetry_sample = self.inlet_telemetry.pull_sample(timeout=0)
            if telemetry_sample[0] != None:
                # 'is_connected' is declared with the first telemetry data, and show battery status immediately
                self.status['is_connected'] = True
                self.status['battery_level'] = telemetry_sample[0][0]


    def update_status_channel_qc(self):
        '''
        This method will continuous update the EEG channel status and quality for Muse, using standard deviation to evaluate the channel quality status.
        '''
        montage = make_standard_montage("standard_1020")

        ch_names = ['TP9', 'AF7', 'AF8', 'TP10']
        ch_types = ['eeg'] * 4
        sfreq = 256
        info = create_info(ch_names, ch_types=ch_types, sfreq=sfreq)

        # IMPORTANT: pull_sample(timeout=0) avoids blocking the execution
        if self.stream_eeg == None:
            print("resolve_byprop: type=EEG")
            self.stream_eeg = resolve_byprop('type', 'EEG', timeout=1)
            self.inlet_eeg = stream_inlet(self.stream_eeg[0])
        # sample once per second (256 samples); more stable than with shorter intervals

        data = self.inlet_eeg.pull_chunk(max_samples=1000000)  # empty the buffer
        time.sleep(1)  # wait to refill. if it crashes during QC, this may be too brief.

        chunk = self.inlet_eeg.pull_chunk(timeout=0, max_samples=100)
        eeg = pd.DataFrame(chunk[0])
        raw = RawArray(eeg.transpose(), info)
        raw.set_montage(montage)

        # For each channel, using the set cutoffs the quality status of the channel will be assigned.
        std_cutoff = 25 # Arbitrary cutoff based on experience with lsl bridge
        upper_cutoff = std_cutoff + 30 # Arbitrary cutoff based on experience
        for ch_pos, channel in enumerate(ch_names, 0):
           
            raw_data, times = raw[channel][:]

            if  np.std(raw_data) < std_cutoff:
                self.status['quality_ch' + str(ch_pos + 1)] = 1
            elif upper_cutoff > np.std(raw_data) >= std_cutoff:
                self.status['quality_ch' + str(ch_pos + 1)] = 2

            else:
                self.status['quality_ch' + str(ch_pos + 1)] = 0

        # Joins each channel quality status into the overall channel summary.
        self.status['channel_summary'] = '_'.join(['g' if self.status['quality_ch' + str(x)]==1 else ('y' if self.status['quality_ch' + str(x)]==2 else 'r') for x in range(1, 5)])
        
    def update_status(self):
        '''
        This method will update the connection status by tooking for an active EEG LSL stream.
        '''
        print(self.status)
        if self.stream_telemetry==None:
            print("resolve_byprop: type=telemetry")
            self.stream_telemetry = resolve_byprop('type', 'Telemetry', timeout=1)
            self.inlet_battery = stream_inlet(self.stream_telemetry[0])


        if self.stream_eeg == None:
            print("resolve_byprop: type=EEG")
            self.stream_eeg = resolve_byprop('type', 'EEG', timeout=1)
            self.inlet_eeg = stream_inlet(self.stream_eeg[0])

        if self.status['is_connected']==False:
            # IMPORTANT: timeout=0 avoids blocking the execution
            # telemetry has low frequency, ~0.1 Hz
            # when there is no new data, and empty array is returned (None, None)
            # if new information came through the channel: ([35.0, 3126.199951171875, 0.0, 0.0], 1637869946.443)
            telemetry_sample = self.inlet_battery.pull_sample(timeout=0)
            if telemetry_sample[0]!=None:
                self.status['is_connected']==True
                print('telemetry_sample:')
                print(telemetry_sample)


    def shutdown(self):
        '''
        This method will close the BlueMuse program.
        '''
        cmd = 'start bluemuse://shutdown'
        subprocess.call(cmd, shell=True)

    def view(self):
        '''
        This method uses muselsl to visualize the LSL stream data created.
        '''
        cmd = 'start /b muselsl view --version 2'
        subprocess.call(cmd, shell=True)

    def open_outlet(self):
        '''
        This method stores a data stream as a StreamInfo object opens a stream outlet which are used to make streaming data available.
        '''
        info = StreamInfo(name='Markers', type='Markers', channel_count=1,
                          channel_format='int32', source_id='sibley_outlet')
        self.outlet = StreamOutlet(info)

    def record_muse_data(self, fn, duration):
        '''
        This method starts a background process that will stream data from the first available Muse
        '''
        recording = Process(target=record, args=(duration, fn))
        recording.start()
        time.sleep(5)
        self.outlet.push_sample(x=[99], timestamp=time.time())
