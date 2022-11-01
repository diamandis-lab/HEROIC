import subprocess
import os
import time
from multiprocessing import Process
import pandas as pd
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
        self.outlet = None

        self.process_bluemuse_stream = None # process that periodically activates device stream in BlueMuse

        self.stream_telemetry = None
        self.inlet_telemetry = None
        self.stream_eeg = None
        self.inlet_eeg = None
        self.info = {'device': 'muse'}
        self.status = {'is_connected': False,
                       'battery_level': None,
                       'quality_ch1': None,
                       'quality_ch2': None,
                       'quality_ch3': None,
                       'quality_ch4': None,
                       'channel_summary': 'n_n_n_n',
                       'ready': False}


    def open_bluemuse(self):
        print("muse.open_stream()")
        # the first command will launch Bluemuse and modify settings (if needed)
        # it seems like Bluemuse stores settings from previous session; we re-do just in case
        # The PGP stream (~60Hz) is sampled to update the variable 'is_connected'
        # The telemetry stream (~0.1Hz) is used to update the variable 'battery_level'
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


    def stream_open(self):

        # the first command will launch Bluemuse and modify settings (if needed)
        # it seems like Bluemuse stores settings from previous session; we re-do just in case
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

        # Lastly, we start the stream
        #cmd = 'start bluemuse://start?streamfirst=true'
        #subprocess.call(cmd, shell=True)
        #print("getting telemetry...")
        #self.bluemuse_stream = Process(target=self.keep_bluemuse_stream)
        #self.bluemuse_stream.start()


    def keep_bluemuse_stream(self):
        cmd = 'start bluemuse://start?streamfirst=true'
        while True:
            print('keep_bluemuse_stream')
            subprocess.call(cmd, shell=True)
            time.sleep(3)

    def stream_close(self):
        if self.process_bluemuse_stream.is_alive():
            self.process_bluemuse_stream.kill()
        if windows_process_running('BlueMuse.exe'):
            windows_taskkill('BlueMuse.exe')

    def update_status_telemetry(self):
        # IMPORTANT: pull_sample(timeout=0) avoids blocking the execution
        # telemetry has low frequency, ~0.1 Hz
        # when there is no new data, and empty array is returned (None, None)
        # if new information came through the channel: ([35.0, 3126.199951171875, 0.0, 0.0], 1637869946.443)
        print('update_status_telemetry')

        # without Muse, and empty stream is created, but not an inlet
        # eventually, when a data-containing stream is found, the inlet is initialized
        if self.inlet_telemetry==None:
            self.stream_telemetry = resolve_byprop('type', 'Telemetry', timeout=1)
            if len(self.stream_telemetry)==1:
                self.inlet_telemetry = stream_inlet(self.stream_telemetry[0])


        if self.inlet_telemetry!=None:
            telemetry_sample = self.inlet_telemetry.pull_sample(timeout=0)
            if telemetry_sample[0] != None:
                # 'is_connected' is declared with the first telemetry data, and show battery status immediately
                self.status['is_connected'] = True
                self.status['battery_level'] = telemetry_sample[0][0]


    def update_status_channel_qc(self):
        # QC based on PSD of Alpha Beta GammaLo bands (Theta excluded, too variable)
        # 'Pass' is given to a channel if median PSD of the three bands is below the 'psd_cutoff'
        iter_freqs = {'Alpha': (8, 14, 3),
                      'Beta': (14, 30, 1.5),
                      'GammaLo': (30, 45, 1)}

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
        chunk = self.inlet_eeg.pull_chunk(timeout=10, max_samples=256)
        eeg = pd.DataFrame(chunk[0])
        raw = RawArray(eeg.transpose(), info)
        raw.set_montage(montage)

        psd = {}
        for freq_name in iter_freqs.keys():
            psds, freqs = psd_multitaper(raw, fmin=iter_freqs[freq_name][0], fmax=iter_freqs[freq_name][1])
            psd[freq_name] = pd.DataFrame(psds).mean(axis=1)
            #print(psd[freq_name])
        # good signal typically < 2,000; wide cutoff to facilitate the beggining of session.
        # signal of moderate quality tends to stabilize with time
        psd_cutoff = 5e4
        for ch_pos in range(4):
            if int(median([psd['Alpha'][ch_pos], psd['Beta'][ch_pos], psd['GammaLo'][ch_pos]])) < psd_cutoff:
                self.status['quality_ch' + str(ch_pos + 1)] = 1
            else:
                self.status['quality_ch' + str(ch_pos + 1)] = 0

        self.status['channel_summary'] = '_'.join(['g' if self.status['quality_ch' + str(x)]==1 else 'r' for x in range(1, 5)])
        '''
        channel_status = {}
        for ch_pos in range(4):
            channel_status[ch_names[ch_pos]] = int(psd['Alpha'][ch_pos])
        print('Alpha: ' + str(channel_status))
        channel_status = {}
        for ch_pos in range(4):
            channel_status[ch_names[ch_pos]] = int(psd['Beta'][ch_pos])
        print('Beta: ' + str(channel_status))
        channel_status = {}
        for ch_pos in range(4):
            channel_status[ch_names[ch_pos]] = int(psd['GammaLo'][ch_pos])
        print('GammaLo' + str(channel_status))
        '''

    def update_status(self):
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
        cmd = 'start bluemuse://shutdown'
        subprocess.call(cmd, shell=True)

    def view(self):
        cmd = 'start /b muselsl view --version 2'
        subprocess.call(cmd, shell=True)

    def open_outlet(self):
        info = StreamInfo(name='Markers', type='Markers', channel_count=1,
                          channel_format='int32', source_id='sibley_outlet')
        self.outlet = StreamOutlet(info)

    def record_data(self, fn, duration):
        # Start a background process that will stream data from the first available Muse
        recording = Process(target=record, args=(duration, fn))
        recording.start()
        time.sleep(5)
        self.outlet.push_sample(x=[99], timestamp=time.time())



    #def push_sample(self, marker, timestamp):
    #    print('Muse.push_sample...' + str(marker[0]) + '...' + str(timestamp))
    #    self.outlet.push_sample(marker, timestamp=timestamp)


