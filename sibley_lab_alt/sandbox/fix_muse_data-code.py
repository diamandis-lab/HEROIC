#sibley/guy.py
#    relevant line: sibley.utils.fix_muse_data(data_file['EEG']))

from sibley.utils import fix_muse_data

def save_session(self):
    global params
    global data_file
    print(data_file)
    params['comments'] = self.textfield_comments.get("1.0", END)[:-1]
    params['session_uuid'] = str(uuid.uuid4())
    session_name = params['timestamp'] + '_' + params['study'] + '_' + params['participant_id']
    Path("output/session/" + session_name).mkdir(parents=True, exist_ok=True)
    session = {'params': params, 'data_file': data_file}
    if 'EEG' in data_file.keys():
        if data_file['EEG'] != 'none':
            session['EEG_marks'] = get_eeg_marks('session_config/' + self.session_config_file[params['session_type']])
    session['task_log'] = self.task_log
    with open('output/info/' + session_name + '.json', 'w') as outfile:
        json.dump(session, outfile, indent=4)
    shutil.copyfile('output/info/' + session_name + '.json', 'output/session/' + session_name + '/session_info.json')
    if 'EEG' in data_file.keys():
        if data_file['EEG'] == 'none':  # session supports EEG capture, but it was executed with "no EEG device"
            open('output/session/' + session_name + '/EEG_none.txt', mode='a').close()  # creates empty file
        else:
            if params['eeg_device'] == 'Muse 2' or params['eeg_device'] == 'Muse S':
                sibley.utils.fix_muse_data(data_file['EEG'])
            # data_file['EEG'] can contain one file (Muse) or multiple (EPOC)
            chunks = data_file['EEG'].split('|')
            for chunk in chunks:
                print('copying...' + chunk)
                filename, file_extension = os.path.splitext(chunk)
                shutil.copyfile(chunk, 'output/session/' + session_name + '/EEG' + file_extension)
    if 'audio' in data_file.keys():
        filename, file_extension = os.path.splitext(data_file['audio'])
        print('data_file[audio]: ' + data_file['audio'])
        shutil.copyfile(data_file['audio'], 'output/session/' + session_name + '/audio' + file_extension)
    if 'keyboard' in data_file.keys():
        filename, file_extension = os.path.splitext(data_file['keyboard'])
        shutil.copyfile(data_file['keyboard'], 'output/session/' + session_name + '/keyboard' + file_extension)
    if 'motion' in data_file.keys():
        filename, file_extension = os.path.splitext(os.path.basename(data_file['motion']))
        shutil.copyfile(data_file['motion'], 'output/session/' + session_name + '/motion' + file_extension)

    zip_folder(dir_home=os.getcwd() + '\\output',
               dir_parent=os.getcwd() + '\\output\\session\\',
               dir_target=session_name,
               file_extension='sbl')
    shutil.rmtree(os.getcwd() + '\\session\\' + session_name)

    self.button_save_session.config(state=DISABLED)
    self.label_save_session.config(text='\u2713', fg='green')
    self.textfield_comments.config(state=DISABLED, bg='grey90')
    print('saving session...')
    os.chdir('../') #  restores base directory, it got switched to output/
    print(os.getcwd())
    

# sibley/utils.py

def fix_muse_data(fname):  # fixes Muse data files where the beginning of the recording lacks the 'marker' column
    with open(fname, 'r') as fp:
        Lines = fp.readlines()
    count = 0
    eeg_new = []  # adding rows to list and then convert to pd.DataFrame for efficiency
    for line in Lines:
        line_curr = line.strip()
        count += 1
        chunks = line_curr.split(',')
        if count == 1:  # fix heading row with 'marker' missing (timestamps, TP9, AF7, AF8, TP10)
            if len(chunks) == 6:  # in case the column exists but it was named something else
                chunks[5] = 'marker'
            if len(chunks) == 5:
                chunks.append('marker')
        if count > 1:  # fix rows with data, missing values in the 'marker' column at the begining of the recording
            if len(chunks) == 5:
                chunks.append('0')
        eeg_new.append(chunks)
    eeg_new = pd.DataFrame(eeg_new[1:], columns=eeg_new[0])
    eeg_new.to_csv(fname, index=False)

