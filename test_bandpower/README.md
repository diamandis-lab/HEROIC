# Test_bandpower

## Requirements
[MNE package](https://mne.tools/stable/index.html): general python library for handling and analysis of EEG data

[YASA package](https://github.com/raphaelvallat/yasa): python library for analysis of sleep-related EEG data

## Important documentation
[YASA notebook: 08_bandpower](https://github.com/raphaelvallat/yasa/blob/master/notebooks/08_bandpower.ipynb)

[MNE tutorial: bandpower on events](https://mne.tools/stable/auto_examples/time_frequency/plot_time_frequency_global_field_power.html)

## File description
**purple_cat_test2.csv** EEG data

**purple_cat_test2_bandpower.csv** powerband intensities

**EEG_bandpower.py** loads raw EEG data and exports the powerband intensities

**01_plot_bandpower.R** plots powerband intensities

**EEG_filter_hilbert_plots.py** loads raw EEG data, performs narroband filtering, Hilbert transforms and produces plots
