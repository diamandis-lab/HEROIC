import time

from pylsl import resolve_byprop, resolve_stream, stream_inlet, resolve_streams, StreamInlet
import pandas as pd
import mne
from mne.time_frequency import psd_welch, psd_multitaper
from mne.channels import make_standard_montage

from sibley.devices.muse import Muse


iter_freqs = {'Theta': (4, 8, 5),
              'Alpha': (8, 14, 3),
              'Beta': (14, 30,1.5),
              'GammaLo': (30,45, 1)}

montage = make_standard_montage("standard_1020")

ch_names = ['AF7', 'TP9', 'AF8' , 'TP10'] # WARNING: possibly wrong order!!!
ch_types = ['eeg'] * 4
sfreq = 256
info = mne.create_info(ch_names, ch_types=ch_types, sfreq=sfreq)

eeg_device = Muse()
#eeg_device.open_bluemuse()


eeg_device.stream_open()  # handled by muselsl
#eeg_device.stream_close()
streams_eeg = resolve_byprop('type', 'EEG', timeout=10)
inlet_eeg = stream_inlet(streams_eeg[0])

while True:
    chunk = inlet_eeg.pull_chunk(timeout=10,max_samples=256)
    eeg = pd.DataFrame(chunk[0])
    raw = mne.io.RawArray(eeg.transpose(), info)
    raw.set_montage(montage)
    #raw.filter(l_freq=1, h_freq=60)

    psd = {}
    for freq_name in iter_freqs.keys():
        psds, freqs = psd_multitaper(raw, fmin=iter_freqs[freq_name][0], fmax=iter_freqs[freq_name][1])
        psd[freq_name] = pd.DataFrame(psds).mean(axis=1)

    psd_cutoff = 5e4
    channel_status = {}
    #for ch_pos in range(4):
    #    if (int(psd['Theta'][ch_pos]) < psd_cutoff and
    #        int(psd['Alpha'][ch_pos]) < psd_cutoff and
    #        int(psd['Beta'][ch_pos]) < psd_cutoff and
    #        int(psd['GammaLo'][ch_pos]) < psd_cutoff):
    #        channel_status[ch_names[ch_pos]] = 1
    #    else:
    #        channel_status[ch_names[ch_pos]] = 0
    for ch_pos in range(4):
        channel_status[ch_names[ch_pos]] = int(psd['Alpha'][ch_pos])

    print(channel_status)


