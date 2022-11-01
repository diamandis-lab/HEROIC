import subprocess
import time
from multiprocessing import Process

from muselsl import record
from pylsl import resolve_byprop, StreamOutlet, StreamInfo, stream_inlet


from sibley.utils import windows_process_running, windows_taskkill


class Muse:
    """Muse 2 or Muse X headband, interface by the muselsl library"""
    def __init__(self):
        self.outlet = None
        self.inlet_eeg_ch1 = None
        self.stream_eeg = None
        self.inlet_battery = None
        self.stream_telemetry = None
        self.info = {'device': 'muse'}
        self.status = {'is_connected': False,
                       'battery_level': -1,
                       'quality_ch1': -1,
                       'quality_ch2': -1,
                       'quality_ch3': -1,
                       'quality_ch4': -1,
                       'quality_summary': 'n_n_n_n',
                       'ready': False}

    def open_bluemuse(self):
        print("muse.open_stream()")
        # the first command will launch Bluemuse and modify settings (if needed)
        # it seems like Bluemuse stores settings from previous session; we re-do just in case
        cmd = 'start bluemuse://setting?key=eeg_enabled!value=true'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=ppg_enabled!value=false'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=gyroscope_enabled!value=false'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=accelerometer_enabled!value=false'
        subprocess.call(cmd, shell=True)
        cmd = 'start bluemuse://setting?key=telemetry_enabled!value=true'
        subprocess.call(cmd, shell=True)


    def open_stream(self):
        # Lastly, we start the stream
        cmd = 'start bluemuse://start?streamfirst=true'
        subprocess.call(cmd, shell=True)
        #print("getting telemetry...")

        #self.streams_eeg = resolve_byprop('type', 'EEG', timeout=10)
        #self.inlet_battery = stream_inlet(self.streams_telemetry[0])
        #self.inlet_eeg_ch1 = stream_inlet(self.streams_eeg[0])



    def update_status(self):
        print("updating status..." + 'device: ' + self.info['device'])
        #if len(self.stream_telemetry) > 0:
        if self.stream_telemetry==None:
            print("resolve_byprop: type=telemetry")
            self.stream_telemetry = resolve_byprop('type', 'Telemetry', timeout=10)
            self.inlet_battery = stream_inlet(self.stream_telemetry[0])

        # IMPORTANT: timeout=0 avoids blocking the execution
        # telemetry has low frequency, ~0.1 Hz
        # when there is no new data, and empty array is returned (None, None)
        # if new information came through the channel: ([35.0, 3126.199951171875, 0.0, 0.0], 1637869946.443)
        telemetry_sample = self.inlet_battery.pull_sample(timeout=0)
        if telemetry_sample[0]!=None:
            print(telemetry_sample)
            self.status = {'is_connected': False,
                           'battery_level': telemetry_sample[0][0],
                           'quality_ch1': 1,
                           'quality_ch2': 1,
                           'quality_ch3': 1,
                           'quality_ch4': 1,
                           'quality_summary': 'g_g_g_g',
                           'ready': True}





        #sample, timestamp = self.inlet_eeg_ch1.pull_sample()
        #print(sample)
        self.status['is_connected'] = True
        self.status['battery_level'] = 100
        self.status['quality_ch1'] = 1
        self.status['quality_ch2'] = 1
        self.status['quality_ch3'] = 1
        self.status['quality_ch4'] = 1
        self.status['ready'] = True
        print(self.status)


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


