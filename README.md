# HEROIC: a platform for remote collection of electroencephalographic data using consumer-grade brain wearables
## Desktop application to collect timestamped data from EEG wearables
![sibley main window](img/eeg_heroic.PNG)
Integrates delivery of experiments and different data capture streams:
* __Low-cost electroencephalogram (EEG):__ 4-channel Muse 2 and Muse S

### Setup
* See `setup_instructions.md` for walkthrough of software installation steps
* Launch the EEG Software: with HEROIC/HEROIC-core/`launch_HEROIC.bat`
* Prepare EEG headband 
* See `HEROIC_Participant_Instructions.pdf` to configure EEG headband and software together

### Experiments
By default, the platform guided participants through one-minute sessions of resting state in both eyes closed and open conditions, three one-minute visual oddball tasks with one-minute meditation sequence in between each visual oddball task. One session will last approximately 7 minutes 
* __Resting State Task:__ A) eyes closed, B) eyes open
* This task uses eyes-closed and eyes-open resting conditions to compare as baseline estimates from the participant’s EEG signal
* __Visual Oddball Task:__ A) mental count of infrequent stimuli
* This task is presents sequences of repetitive stimuli that are infrequently interrupted by a deviant "surprise" stimulus
* __Meditation:__ A) mental relaxation
* These experiments can be customized in the session configuartions to adjust the duration and number of experiments in a single session


#### EEG traces of a Muse 2 headband
![eeg muse](img/eeg_muse.png)
