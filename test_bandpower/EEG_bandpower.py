import mne
import yasa
import numpy as np
import pandas as pd
from scipy.signal import welch


data = np.genfromtxt('purple_cat_test2.csv', delimiter=',')
data = np.transpose(data)



ch_names = ['CH1', 'CH2', 'CH3', 'CH4']
ch_types = ['eeg', 'eeg', 'eeg', 'eeg']
sfreq = 256  # Hz sampling rate

# Create the info structure needed by MNE
info = mne.create_info(ch_names=ch_names, ch_types=ch_types, sfreq=sfreq)


raw = mne.io.RawArray(data, info)

raw.pick_types(eeg=True)
# Apply a bandpass filter between 0.5 - 45 Hz
raw.filter(0.5, 45)

# Extract the data and convert from V to uV
data = raw._data * 1e6
sf = raw.info['sfreq']
chan = raw.ch_names

# Let's have a look at the data
print('Chan =', chan)
print('Sampling frequency =', sf, 'Hz')
print('Data shape =', data.shape)

win = int(4 * sf)  # Window size is set to 4 seconds
freqs, psd = welch(data, sf, nperseg=win, average='median')  # Works with single or multi-channel data

yasa.bandpower_from_psd(psd, freqs, ch_names=chan)


events = mne.make_fixed_length_events(raw, duration=15)


win = int(4 * sf)  # Window size is set to 4 seconds
freqs, psd = welch(data[:, 0:3840], sf, nperseg=win, average='median')  # Works with single or multi-channel data
yasa.bandpower_from_psd(psd, freqs, ch_names=chan)

pos_event = events[:, 0]


col_names = ['Chan', 'Delta', 'Theta', 'Alpha', 'Sigma', 'Beta', 'Gamma', 'TotalAbsPow', 'FreqRes', 'Relative']
bandpower = pd.DataFrame(columns=col_names)


for curr in list(range(pos_event.size-1)):
    freqs, psd = welch(data[:, pos_event[curr]:pos_event[curr+1]], sf, nperseg=win, average='median')  # Works with single or multi-channel data
    res = yasa.bandpower_from_psd(psd, freqs, ch_names=chan, relative=True)
    res['epoch_no'] = curr
    res['from'] = pos_event[curr]+1
    res['to'] = pos_event[curr+1]
    bandpower = bandpower.append(res)


bandpower.to_csv('purple_cat_test2_bandpower.csv', index=False)

