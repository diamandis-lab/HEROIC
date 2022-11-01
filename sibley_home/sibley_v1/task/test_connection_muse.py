from pylsl import resolve_byprop, resolve_stream, stream_inlet, resolve_streams, StreamInlet
import pandas as pd
import mne
from mne.time_frequency import psd_welch, psd_multitaper
from mne.channels import make_standard_montage

from sibley.devices.muse import Muse

eeg_device = Muse()
eeg_device.open_bluemuse()


eeg_device.open_stream()  # handled by muselsl
# streams = resolve_byprop('type', 'EEG', timeout=10)  # pylsl
# eeg_device.stream
streams_eeg = resolve_byprop('type', 'EEG', timeout=10)
# streams_telemetry = resolve_byprop('type', 'telemetry', timeout=10)


streams_eeg = resolve_byprop('type', 'EEG', timeout=10)

inlet_eeg = stream_inlet(streams_eeg[0])

chunk = inlet_eeg.pull_chunk(timeout=0.0,max_samples=256)

eeg = pd.DataFrame(chunk[0])


#eeg_device.record_data(fn=data_file['EEG'], duration=self.session_duration[params['session_type']])


ch_names = ['AF7', 'TP9', 'AF8' , 'TP10'] # WARNING: possibly wrong order!!!
ch_types = ['eeg'] * 4
sfreq = 256
info = mne.create_info(ch_names, ch_types=ch_types, sfreq=sfreq)

raw = mne.io.RawArray(eeg.transpose(), info)
montage = make_standard_montage("standard_1020")
raw.set_montage(montage)

raw.filter(l_freq=1, h_freq=60)

iter_freqs = {'Theta': (4, 8, 5),
              'Alpha': (8, 14, 3),
              'Beta': (14, 30,1.5),
              'GammaLo': (30,45, 1)}

freq_name = "Theta"


psds, freqs = psd_multitaper(raw, fmin=iter_freqs[freq_name][0], fmax=iter_freqs[freq_name][1])

raw.plot()
raw.plot_psd()