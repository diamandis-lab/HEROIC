# How to configure EEG-station (Windows 10)

### Summary

EEG-station is a Windows 10 computer containing the software necessary to design and run EEG experiments.

### Auxiliary tools (Install these first)

Software| Link | Comments
--------| ---- | -------
Git for Windows |[Download](https://git-scm.com/download/win)|Code management tool. Add to Path: `C:\Program Files\Git\mingw64\bin\curl`, used to communicate with couchdb.
cmake 3.19.4|[Download](https://cmake.org/download/)|Tool for building software (needed for liblsl)
Visual Studio 2017 Community (15.9)|[Download](https://visualstudio.microsoft.com/vs/older-downloads)|Environment and tools for building software in Windows. During the installation process, select the following modules: .NET desktop development, Desktop development with C++, and Universal Windows Platform development. (needed for liblsl)
liblsl|[install instructions](https://ws-dl.blogspot.com/2019/07/2019-07-15-lab-streaming-layer-lsl.html)|important library to add "marks" in the EEG data via the LSL protocol.
BlueMuse | [Download](https://github.com/kowalej/BlueMuse/releases/download/v2.1/BlueMuse_2.1.0.0.zip) [Documentation](https://github.com/kowalej/BlueMuse) | Windows 10 app to stream data from Muse EEG headsets. **Install instructions:** after download/uncompress, right-click on "InstallBlueMuse" and select "Run with PowerShell"; follow the prompts; a Windows configuration window will open, the option "developer mode" needs to be selected; finish the install process
SWIG 4.0.2 | [Download](http://prdownloads.sourceforge.net/swig/swigwin-4.0.2.zip) | Code wrapper, required by psychopy. Unzip, copy to C:/Program Files/ and **add to the PATH environment variable.**
fmedia|[Download](https://stsaz.github.io/fmedia/)|Used to record environment audio using the computer's microphone. Unzip and copy to C:/Program Files(x86)/
VLC media player|[Download](https://www.videolan.org/vlc/download-windows.html)|Used to play session's video
nircmd | [Download](http://www.nirsoft.net/utils/nircmd-x64.zip)|Tool to execute Windows commands. Used to hide the two windows of the BlueMuse application. Unzip and topy to C:/Program Files/

### Python environment

Software | Link | Comments
---------|------|---------
Python 3.8.9|[Download](https://www.python.org/downloads) | Phython runtime and SDK. Avoid using the latest branch (as of this writing 3.9.4). PsychoPy contains many dependencies and the development of some may have not reached the latest version
python venv|create venv|`mkdir sibley_38; python -m venv sibley_38`. To activate: `sibley/Scripts/activate.bat`. **Execute library installs within this venv**. `pip install wheel` (Optionally, update wheel following the instructions).
precompiled|[Page](https://www.lfd.uci.edu/~gohlke/pythonlibs/)|**This step is not required when using Conda.** Download precompiled wheels for Windows [pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and [pytables](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables). Install by doing: `pip install pyaudio...whl`.
PsychoPy 2020.2.3 | [Documentation](https://www.psychopy.org/api/api.html) | Python library for running experiments in behavioural sciences. `pip install psychopy==2020.2.3`. **More recent versions fail to install in Windows**.
vispy|[Documentation](https://vispy.org/)|Visualization library in Python `pip install vispy` (required by muselsl view -v2)
mne|[Documentation](https://vispy.org/)|EEG signal analysis library in Python `pip install mne` (required by muselsl view -v2)
Muse LSL|[github](https://github.com/alexandrebarachant/muse-lsl)|`pip install muselsl` Visualization of the data stream from BlueMuse by executing `muselsl view -v2`
ffpyplayer|[Documentation](https://matham.github.io/ffpyplayer/index.html)|Python library used to play audio `pip install ffpyplayer`
playsound 1.2.2|[Documentation](https://github.com/TaylorSMarks/playsound)|Python sound library `pip install playsound==1.2.2`. Newer versions (i.e. 1.3.0) produce an error due to a bug in the library.
sibley EEG|copy files|main application

### Optional

Software | Link | Comments
---------|------|---------
Dropbox | [Download](https://www.dropbox.com/downloading)| Cloud data storage service
WSL2 kernel update | [Download](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi) | Windows subsystem for Linux, needed for Docker. After installin, "Run PowerShell as administrator", and execute `wsl --set-default-version 2`
Docker | [Download](https://www.docker.com/docker-for-windows/install)|Virtualization tool. 

