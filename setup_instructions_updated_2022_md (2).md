# How to configure EEG-station (Windows 10)

### Summary

EEG-station is a Windows 10 computer containing the software necessary to design and run EEG experiments.
The following set up instructions should take precedence over instructions provided on external links.
Most recently successful in setting up sibley_38 on a Lenovo Thinkpad Yoga 260 (Windows 10 Pro) and Dell Latitude E7440 systems on September 16, 2022.

### Auxiliary tools (Install these first)

Software| Link | Comments
--------| ---- | -------
Git for Windows |[Download](https://git-scm.com/download/win)|Code management tool. Download the latest (2.38.0) 64-bit version of Git for Windows, as of October 6, 2022. During installation, select defaults during setup and select available text editor for the computer by preference (ie. Notepad). Add to Path: `C:\Program Files\Git\mingw64\bin\curl` and `C:\Program Files\Git\cmd\`, used to communicate with couchdb.
cmake 3.19.4|[Download](https://www.cmake.org/files/v3.19/cmake-3.19.4-win64-x64.msi)|Tool for building software (needed for liblsl). Download the .MSI file. The CMake folder should be set up here: `C:/Program Files/CMake` and add CMake to the system PATH for all users. 
Visual Studio 2017 Community (15.9)|[Download](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&rel=15)|Environment and tools for building software in Windows. During the installation process, select the following modules: .NET desktop development, Desktop development with C++, and Universal Windows Platform development. (needed for liblsl)
liblsl|[install instructions](https://ws-dl.blogspot.com/2019/07/2019-07-15-lab-streaming-layer-lsl.html)|important library to add "marks" in the EEG data via the LSL protocol. **Installing Qt**: install Qt [qt-unified-windows-x64-4.4.1-online](https://download.qt.io/archive/online_installers/4.4/qt-unified-windows-x64-4.4.1-online.exe ), sign in or sign up for a Qt Account. During the installation process in the Select Components, on the right side, check all boxes (Archive, LTS, Latest supported releases, Preview) for the necessary to appear. **Installing Lab Streaming Layer**: format Step 5 in a single command and specify Qt details (`cmake C:\labstreaminglayer -G "Visual Studio 15 2017 Win64" -DLSL_LSLBOOST_PATH=C:\labstreaminglayer\LSL\liblsl\lslboost -DQt5_DIR=C:\Qt\5.15.2\msvc2019_64\lib\cmake\Qt5 -DBOOST_ROOT=C:\boost_1_67_0\stage\lib -DLSLAPPS_LabRecorder=ON -DLSLAPPS_XDFBrowser=ON -DLSLAPPS_Examples=ON -DLSLAPPS_Benchmarks=ON -DLSLAPPS_BestPracticesGUI=ON`), Step 8 (`cmake -G "Visual Studio 15 2017 Win64" -S . -B C:/labstreaminglayer/build`) then ignore error MSB1009 and remaining installation steps
BlueMuse | [Download](https://github.com/kowalej/BlueMuse/releases/download/v2.2.0.0/BlueMuse_2.2.0.0.zip) [Documentation](https://github.com/kowalej/BlueMuse) | Windows 10 app to stream data from Muse EEG headsets. **Install instructions:** after download/uncompress, right-click on "InstallBlueMuse" and select "Run with PowerShell"; follow the prompts; a Windows configuration window will open, the option "developer mode" needs to be selected; finish the install process
SWIG 4.0.2 | [Download](http://prdownloads.sourceforge.net/swig/swigwin-4.0.2.zip) | Code wrapper, required by psychopy. Unzip, copy to C:/Program Files/ and **add to the PATH environment variable.**
fmedia|[Download](https://stsaz.github.io/fmedia/)|Used to record environment audio using the computer's microphone. Unzip and copy to C:/Program Files(x86)/
VLC media player|[Download](https://www.videolan.org/vlc/download-windows.html)|Used to play session's video
nircmd-x64 | [Download](https://www.nirsoft.net/utils/nircmd-x64.zip)|Tool to execute Windows commands. Used to hide the two windows of the BlueMuse application. Unzip and copy to C:/Program Files/

### Python environment

Software | Link | Comments
---------|------|---------
Python 3.8.9|[Download](https://www.python.org/ftp/python/3.8.9/python-3.8.9-amd64.exe) | Python runtime and SDK. Avoid using the latest branch (as of this writing 3.9.4). PsychoPy contains many dependencies and the development of some may have not reached the latest version. Note: during installation select add to path.
python venv|create venv|`mkdir sibley_38` and `python -m venv sibley_38`. Change directory to: `C:\Users\Lenovo\sibley_38\Scripts` To activate environment: `activate`. **Execute library installs within this venv**. `pip install wheel` (Optionally, update wheel following the instructions). **pip 20.2.3**: `pip --version` and `python -m pip install==20.2.3` Note: for ease of access to sibley_38 in File Folder, pin the 'sibley_38' folder to Quick Access.
precompiled PyAudio & PyTable|[Page](https://www.lfd.uci.edu/~gohlke/pythonlibs/)|**This step is not required when using Conda.** Download precompiled wheels for Windows [PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and [tables‑3.7.0‑cp38‑cp38‑win_amd64.whl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables), and move the files to `C:\Users\admin_name\sibley_38`. Use command `cd ..` to change directory to `C:\Users\Lenovo\sibley_38`, then install by: `pip install PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl` and `pip install tables‑3.7.0‑cp38‑cp38‑win_amd64.whl`
PsychoPy 2020.2.3 | [Delete me](https://www.psychopy.org/api/api.html) | Python library for running experiments in behavioural sciences. `pip install psychopy==2020.2.3`. **More recent versions fail to install in Windows**.
vispy|[Documentation](https://vispy.org/)|Visualization library in Python `pip install vispy` (required by muselsl view -v2)
mne|[Documentation](https://vispy.org/)|EEG signal analysis library in Python `pip install mne` (required by muselsl view -v2)
Muse LSL|[github](https://github.com/alexandrebarachant/muse-lsl)|`pip install muselsl==2.1.0` Visualization of the data stream from BlueMuse by executing `muselsl view -v2` (this command was unnescessary). Then `pip install pylsl==1.10.5`
ffpyplayer|[Documentation](https://matham.github.io/ffpyplayer/index.html)|Python library used to play audio `pip install ffpyplayer`
playsound 1.2.2|[Documentation](https://github.com/TaylorSMarks/playsound)|Python sound library `pip install playsound==1.2.2`. Newer versions (i.e. 1.3.0) produce an error due to a bug in the library.
sibley EEG|copy files or [Download eeg-station-main ZIP](https://github.com/diamandis-lab/eeg-station.git) |main application from private GitHub repository (get invitation from owner)

### Optional

Software | Link | Comments
---------|------|---------
Dropbox | [Download](https://www.dropbox.com/downloading)| Cloud data storage service
WSL2 kernel update | [Download](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi) | Windows subsystem for Linux, needed for Docker. After installin, "Run PowerShell as administrator", and execute `wsl --set-default-version 2`
Docker | [Download](https://www.docker.com/docker-for-windows/install)|Virtualization tool.
7-Zip |[Download 22.01](https://www.7-zip.org/a/7z2201-x64.exe)| Extract .sbl files
Google Chrome |[Download](https://www.google.com/chrome/thank-you.html?installdataindex=empty&statcb=0&defaultbrowser=0&brand=RXQR#)| Use web browser Google Drive to upload data files

### Path Contents
Go to View Advanced System Settings, Environmental Variables, Path, and Edit:

 | Path |
 |---------|
| C:\Users\Lenovo\AppData\Local\Programs\Python\Python38\Scripts\ |
|C:\Users\Lenovo\AppData\Local\Programs\Python\Python38\|
|%USERPROFILE%\AppData\Local\Microsoft\WindowsApps|
|C:\Program Files\Git\mingw64\bin\curl|
|C:\Program Files\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin|
|C:\Program Files\nircmd|
|C:\labstreaminglayer\build\install.vcxproj|
| **Dell** Path: %USERPROFILE%\.dotnet\tools|
|C:\boost_1_67_0\boost_1_67_0\stage\lib|

### Updates within sibley_38:

 | Issue | Files | Updates and Source Code |
 |---|---|---|
 | `sibley_38` Directory Organizing | eeg_station_main.zip, `\sibley_38\` | extract ZIP and move to `sibley_38` directory, copy everything from `sibley_38\sibley_38` to `sibley_38` directory, rename `sibley_38\sibley_38` to `sibley_38\sibley`. See screenshots taken from the L001 file folder for proper folder set up. |
 |`sibley_2.0` |[Download & extract](https://github.com/IngridCampbell/sibley_2.0/archive/refs/heads/dev.zip)| For sibley_2.0, download a ZIP from the dev branch or in command prompt `git clone https://github.com/IngridCampbell/sibley_2.0.git` with `git branch --set-upstream-to=origin/dev` and `git pull`
 | Launching sibley | C:\Users\Lenovo\sibley_38\sibley\ `launch_sibley.bat` | `cd sibley_38` and `mkdir session_logs` and edit: `set PATH_SIBLEY=C:\Users\admin_name\sibley_38\sibley`, `cmd /k "..\Scripts\activate.bat & python .\main.py > ..\session_logs\%LOG_NAME% 2>&1"` |
 | Data Problem (Summer 2022 Bug) & Save Session | C:\Users\Lenovo\sibley_38\sibley\sandbox\ `\fix_muse_data-code.py` | Copy the `fix_muse_data` function. Copy the `save_session` functions|
 | |C:\Users\Lenovo\sibley_38\sibley\sibley `\utils.py` | Paste `fix_muse_data` function & save.  Copy **Code 2** and paste in the end of function `fix_muse_data`, watch import statement `import pandas as pd`, and the indentations. Save. |
 | |C:\Users\Lenovo\sibley_38\sibley\sibley `\gui.py` | Paste and replace current `save_session` function being especially careful with indentations, update `from sibley.utils import zip_folder, fix_muse_data`. Replace the `sibley.utils.fix_muse_data(data_file['EEG'])` line with `fix_muse_data(data_file['EEG'])` & save |
 |Visual Problem (Summer 2022 Bug)| C:\Users\Lenovo\sibley_38\sibley\sibley\task `p300_visual_color_circles.py` | Within function `run_session` write new function `show_cross(win)` (above the function `show_stimulus`. Cut the code below in **Code 1** from function `show_stimulus` and paste into the function `show_cross`. Change `color=custom_color['black']`  to `color=custom_color['grey']`. Call the function `show_cross(win=win)` after the `print('round=' + str(pos) + ' color=' + color_curr) # include blank line after` statement. Save changes. Note: With these changes the system should be able to run a session though it may be unable to properly save session. |
 |Visual Circles Rarity | C:\Users\Lenovo\sibley_38\sibley\sibley\task `p300_visual_color_circles.py` | Change rarity of green circles on visual test to `percent_green = 90`. Save. |
 | | C:\Users\Lenovo\sibley_38\sibley\session_config `p300_visual_color_circles.json` | Open in Visual Studio and change `"percent_green": 90` for all 3 parameters. **Check this on the Dell and Dell 2022.** Save. |
 | sibley Control Panel Window Pop Up During Session |C:\Users\Lenovo\sibley_38\sibley\sibley `\gui.py` |In the `start_session` function,  add `self.root.withdraw()` after the `print('start_session’)` line to hide the control panel window. Then, add `self.root.deiconify()`, after the `mywin.close()` line to show the control panel window again. |
 |Troubleshooting |  | Be careful with indentations. If there are necessary updates, push working progress to the main repository. |
 | Launch sibley shortcut| C:\Users\Lenovo\sibley_38\sibley `launch_sibley.bat` | Create launch_sibley shortcut to an accessible location on system (`C:\Users\Lenovo\Desktop`) |

**Code 1**

    def show_cross(win):
        text_cross = visual.TextStim(win=win, text='\u00D7', color=custom_color['black'], 	colorSpace='hex', height=8.6, pos=[0, 0.5])
        text_cross.draw()
        win.flip()
        core.wait(random.randint(300, 500) / 1000)
        win.flip()
	
**Code 2**

    import pandas as pd
	#
    # removes malformed rows, possibily due to stream drops and reconnects
    # reopens .csv, drops lines with wrong number of columns, saves clean .csv
    with open(fname, 'r') as fp:
        lines = fp.readlines()
    lines = [x.replace('\n', '') for x in lines] # removes return character at the end of each line
    lines_clean = [line.split(',') for line in lines if len(line.split(',')) == 6]
    eeg_clean = pd.DataFrame(lines_clean[1:], columns=lines_clean[0])
    if len(lines_clean) < len(lines):
        eeg_clean.to_csv(fname, index=False)
	
 
 ### Set Up Completed
If the following are accomplished then the EEG-station is properly configure on the system:

 | Test | Evaluate | 
 |---------|
 | Run a P300 Visual Test | Successful Launch EEG Session & Save Session, blue circles should appear ~10% throughout the visual circles test |
  | Check Session Logs | Launch EEG Session & Save Session should be stored in C:\Users\Lenovo\sibley_38\session_logs with File(s) for each run (ie. Fri) |
  |Check Sessions Output | C:\Users\Lenovo\sibley_38\sibley\output\session |
 | Data Stored | Check if data stored as .sbl, download 7-zip to extract file as folder|
