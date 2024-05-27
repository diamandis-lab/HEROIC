class DefaultEEG:
    """Generic eeg with non-working status"""
    def __init__(self):
        self.info = {'device': 'default'}
        self.status = {'is_connected': False,
                       'battery_level': -1,
                       'quality_ch1': -1,
                       'quality_ch2': -1,
                       'quality_ch3': -1,
                       'quality_ch4': -1,
                       'ready': False}


    def update_status(self):
        print("updating status..." + 'device: ' + self.info['device'])

