import subprocess
import time

from pylsl import StreamInfo, StreamOutlet
from sibley.utils import windows_process_running


class EPOC:
    """EPOC X headband"""

    def __init__(self):
        self.outlet = None

    def open_outlet(self):
        # duration not  used, just included for compatibility with muse.start
        if not windows_process_running("EmotivPro.exe"):
            cmd = 'start /b C:/PROGRA~1/EmotivApps/EmotivPro.exe'
            subprocess.call(cmd, shell=True)
        print('EPOC.start')
        info = StreamInfo(name='Markers', type='Markers', channel_count=1,
                          channel_format='int32', source_id='sibley_outlet')
        self.outlet = StreamOutlet(info)
        # time.sleep(5)  # no need to wait as configure EmotivPro session comes next
        self.outlet.push_sample(x=[99], timestamp=time.time())

    #def push_sample(self, marker, timestamp):
    #    print('EPOC.push_sample...' + str(marker[0]) + '...' + str(timestamp))
    #    self.outlet.push_sample(marker, timestamp=timestamp)

