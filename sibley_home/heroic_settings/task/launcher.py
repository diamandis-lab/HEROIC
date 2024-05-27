import subprocess
import time



cmd = ['python', 'sibley/task/speech_recognition_stream.py']



#try:
#    r = subprocess.run(cmd, timeout=10, shell=True, capture_output=False)
#except subprocess.TimeoutExpired as e:
#    print(e)

import subprocess
from subprocess import Popen
import time
from sibley.task.media import record_audio


record_audio("test_autio.wav", '60')

cmd = ['python', 'sibley/task/speech_recognition_stream.py']
t_start = time.time()
with Popen(cmd, shell=True) as process:
    print(f"Just launched server with PID {process.pid}")
    for s in range(10):
        time.sleep(1)
        if time.time() - t_start > 10:
            print("I'm killing you!")
            subprocess.run('taskkill /F /PID ' + str(process.pid))


#taskkill /F /PID 19516
