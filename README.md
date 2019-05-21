This program is based on the work of Sundar Krishnan

Detailed writeup can be found here:
https://towardsdatascience.com/how-to-use-google-speech-to-text-api-to-transcribe-long-audio-files-1c886f4eb3e9


Improvements:
Made it work. I had a lot of issues with audio codecs
Added support for m4a
Added an webinterface


Required:
Google account see Sundar Krishnan writeup
apt-get install ffmpeg libavcodec-extra
pip install --upgrade google-cloud-speech
pip install --upgrade google-cloud-storage
pip install pydub
pip install flask