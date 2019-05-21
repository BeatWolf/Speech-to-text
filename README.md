This program is based on the work of Sundar Krishnan

Detailed writeup can be found here:<br>
https://towardsdatascience.com/how-to-use-google-speech-to-text-api-to-transcribe-long-audio-files-1c886f4eb3e9


<h2>Improvements:</h2><br>
Made it work. I had a lot of issues with audio codecs<br>
Added support for m4a<br>
Added an webinterface<br>


<h2>Required:</h2><br>
Google account see Sundar Krishnan writeup <br>
apt-get install ffmpeg libavcodec-extra<br>
pip install --upgrade google-cloud-speech<br>
pip install --upgrade google-cloud-storage<br>
pip install pydub<br>
pip install flask<br>
