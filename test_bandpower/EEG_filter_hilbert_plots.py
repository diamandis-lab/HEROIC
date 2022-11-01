import numpy as np
import mne


data = np.genfromtxt('purple_cat_test2.csv', delimiter=',')
data = np.transpose(data)



ch_names = ['CH1', 'CH2', 'CH3', 'CH4']
ch_types = ['eeg', 'eeg', 'eeg', 'eeg']
sfreq = 256  # Hz sampling rate

# Create the info structure needed by MNE
info = mne.create_info(ch_names=ch_names, ch_types=ch_types, sfreq=sfreq)


raw = mne.io.RawArray(data, info)


raw.plot()


iter_freqs = [
    ('Theta', 4, 7),
    ('Alpha', 8, 12),
    ('Beta', 13, 25),
    ('Gamma', 30, 45)
]

theta = raw
theta.filter(4, 7, n_jobs=1, picks='all')
theta.apply_hilbert(envelope=True, picks='all')
theta.plot(title='theta')


alpha = raw
alpha.filter(8, 12, n_jobs=1, picks='all')
alpha.apply_hilbert(envelope=True, picks='all')
alpha.plot(title='alpha')


beta = raw
beta.filter(13, 25, n_jobs=1, picks='all')
beta.apply_hilbert(envelope=True, picks='all')
beta.plot(title='beta')



gamma = raw
gamma.filter(30, 45, n_jobs=1, picks='all')
gamma.apply_hilbert(envelope=True, picks='all')
gamma.plot(title='gamma')
