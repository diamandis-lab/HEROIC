# Methods for speech-to-text

## DeepSpeech
### test_16000-deepspeech.json
docker run -it --rm -v /data/EEG:/data/EEG deepspeech:210506 /bin/bash

## Google Cloud Speech
### Install Cloud SDK (gcloud command tool)
Follow the [instructions](https://cloud.google.com/sdk/docs/install#deb), available for different OS
### Authenticate
Method 1 (with browser): `gcloud auth login` opens the Google authentication dialog
Method 2 (service account): create a Google Cloud service account with permissions for the Transcribe API and for the Google Store bucket. Then, create a new KEY (.json) using the console, download the key, and then execute `gcloud auth activate-service-account sevice-account-name@myproject-123456.iam.gserviceaccount.com --key-file=auth_key.json --project=testproject`
### test_16000-google.json
```
gsutil cp data/sbl/session_files/20210730-124349_default_gold-dog/audio.wav gs://sibley-speech/wav/20210730-124349_default_gold-dog/audio.wav
gcloud ml speech recognize-long-running \
    gs://sibley-speech/wav/20210730-124349_default_gold-dog/audio.wav \
     --language-code='en-US' --async \
	 --include-word-time-offsets \
	 --hints=['white','yellow','red','green','blue','pink'] \
	 --max-alternatives=5
   
 # server response
Check operation [operations/2907934928349389694] for status.
{
  "name": "2907934928349389694"
}
# check if the job is completed before saving
gcloud ml speech operations describe 2907934928349389694 > 20210506-212721_default_racoon.json
gsutil cp 20210506-212721_default_racoon.json gs://sibley-speech/speech-to-text/
```

## Azure Speech
Audio files should be in .wav format (16000 Hz)
```
# in the host
docker pull mcr.microsoft.com/dotnet/sdk:3.1
docker exec -it --rm -name azure_speech mcr.microsoft.com/dotnet/sdk:3.1 /bin/bash
# inside the container
dotnet tool install --global Microsoft.CognitiveServices.Speech.CLI
export PATH="$PATH:/root/.dotnet/tools"
spx config @key --set [SPEECH-SERVICE-KEY, from Azure Speech dashboard]
spx config @region --set eastus
# in a separate command prompt in the host
docker commit azure_speech azure/speech:01
# inside the container
exit
# in the host
docker run -it --rm -v /path/local_folder:/data azure/speech:01 /bin/bash
# inside the container
spx recognize --file test_16000.wav --output batch json
cat output.test_16000.132647978147089121.json
```

## Amazon Transcribe
Audio files should be in .wav format (16000 Hz)
Using AWS's web interface:
* In Amazon S3 (files storage)
  * create new bucket (i.e. sibley_eeg)
  * create folder: `s3://sibley_eeg/wav`
  * create folder: `s3://sibley_eeg/transcribe`
  * Upload audio file to the wav folder
* In Amazon Transcribe
  * Optional: create Custom vocabulary (text file with words of interest, one per line)
  * Create Transcription job: specify the S3 route of the input file, and under Output data > Customer specified bucket, specify the S3 route of the output .json file; optional: under Customization > Custom vocabulary







