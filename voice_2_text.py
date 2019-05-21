
import os
import wave
import io
import os
import time
import sys
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types
from flask import Flask, flash, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from google.cloud import storage
from pydub import AudioSegment

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

filepath = "/root/Speech-to-text/audio/"
output_filepath = "/root/Speech-to-text/text/"
UPLOAD_FOLDER = '/root/Speech-to-text/uploads'
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'm4a'])
bucket_name = 'voice_upload'
Language_code = 'nl-NL' # https://cloud.google.com/speech-to-text/docs/languages


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            uploaded_file_path = str(app.config['UPLOAD_FOLDER']+"/"+filename)
            print "File uploaded: \t" + uploaded_file_path

            exists = os.path.isfile(output_filepath + filename.split('.')[0] + '.txt')
            if exists:
                print "File already exists serving that one: \t"
                print output_filepath + filename.split('.')[0] + '.txt'
                return send_file(output_filepath + filename.split('.')[0] + '.txt')

            else:
                transcript = google_transcribe(uploaded_file_path)
                print "Saving Transcript"
                transcript_filename = filename.split('.')[0] + '.txt'
                write_transcripts(transcript_filename, transcript)
                return send_file(output_filepath + transcript_filename)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new interview</h1>
    <h2>De laad tijd van deze pagina is ongeveer de lengte van het interview!!!!</h2>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''



def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':
        sound = AudioSegment.from_mp3(audio_file_name)
    if audio_file_name.split('.')[1] == 'm4a':
        sound = AudioSegment.from_file(audio_file_name)
    if audio_file_name.split('.')[1] == 'wav':
        sound = AudioSegment.from_file(audio_file_name)

    wav_file_path = filepath+audio_file_name.split("/")[-1].split('.')[0] + '.wav'
    sound = sound.set_channels(1)
    sound = sound.set_sample_width(2)
    sound.export(wav_file_path, format="wav")
    return wav_file_path


def frame_rate_channel(audio_file_name):
    wave_file = wave.open(audio_file_name, "rb")
    frame_rate = wave_file.getframerate()
    channels = wave_file.getnchannels()
    return frame_rate,channels


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()


def google_transcribe(uploaded_file_path):
    print "Converting: \t" + uploaded_file_path.split("/")[-1]
    wav_file_path = mp3_to_wav(uploaded_file_path)
    print "Converted: \t" + wav_file_path.split("/")[-1]
    print "Checking frame rate: \t", wav_file_path.split("/")[-1]
    frame_rate, channels = frame_rate_channel(wav_file_path)
    wav_name = wav_file_path.split("/")[-1]

    print "Uploading blob: \t",wav_name
    upload_blob(bucket_name, wav_file_path, wav_name)

    print "Starting Transcripting: \t",wav_name
    gcs_uri = 'gs://'+bucket_name+'/' + wav_name
    transcript = ''
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=frame_rate,
        language_code=Language_code,
        enable_speaker_diarization=True,
        diarization_speaker_count=2)

    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)
    result = response.results[-1]
    words_info = result.alternatives[0].words

    tag = 1
    speaker = ""

    for word_info in words_info:
        if word_info.speaker_tag == tag:
            speaker = speaker + " " + word_info.word
        else:
            transcript += "speaker {}: {}".format(tag, speaker) + '\n'
            tag = word_info.speaker_tag
            speaker = "" + word_info.word

    transcript += "speaker {}: {}".format(tag, speaker)

    print "Deleting blob: \t", wav_name
    delete_blob(bucket_name, wav_name)
    return transcript

def write_transcripts(transcript_filename,transcript):
    f= open(output_filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close()


# if __name__ == "__main__":
#     for audio_file_name in os.listdir(UPLOAD_FOLDER):
#         exists = os.path.isfile(output_filepath + audio_file_name.split('.')[0] + '.txt')
#         if exists:
#             pass
#         else:
#             transcript = google_transcribe(audio_file_name)
#             transcript_filename = audio_file_name.split('.')[0] + '.txt'
#             write_transcripts(transcript_filename,transcript)

if __name__ == "__main__":
   app.run(debug=True, host="0.0.0.0", port=8005, threaded=True)
