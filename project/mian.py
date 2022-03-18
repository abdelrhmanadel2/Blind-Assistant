import wave
import threading
import os
import response
import glob
import re
import sys
import time
import io
# from google.cloud import speech
import pyaudio
from six.moves import queue
import speak
import constants
import speech_recognition as sr

# Audio recording parameters
STREAMING_LIMIT = 3000  
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"

recognized_text = '' 
def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))


os.environ['GOOGLE_APPLICATION_CREDENTIALS']='project\credential.json'
RESPEAKER_RATE = 16000                  # Sample rate of the mic.
RESPEAKER_CHANNELS = 1                  # Number of channel of the input device.
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 0                     # run the check_device_id.py to get the mic index.
CHUNK = 1024                            # Number of frames per buffer.
WAVE_OUTPUT_FILEPATH = "ramdisk/"  # Directory location ocation of all the output files.
recognized_text=''        # Global variable for storing  audio converted text
                   

Recognizer = sr.Recognizer()

class voice:
    """
    __init__ method will create pyaudio stream object
    for the entire session. This stream will be used
    every time for voice detection from microphone.
    """
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            rate=RESPEAKER_RATE,
            format=pyaudio.paInt16,
            channels=RESPEAKER_CHANNELS,
            input=True,
            frames_per_buffer=CHUNK)

    """
    process() method reads data from pyaudio stream for given duration.
    After read, it creates audio frame and save it to .wav file.
    it generates new WAV file every time it gets called.
    """
    def process(self, RECORD_SECONDS):
        frames = []
        for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        out_filename = WAVE_OUTPUT_FILEPATH + str(time.time()) + ".wav"
        wf = wave.open(out_filename, 'wb')
        wf.setnchannels(RESPEAKER_CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(RESPEAKER_WIDTH)))
        wf.setframerate(RESPEAKER_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return out_filename

    """
    voice_command_processor() method reads data from .wav file and convert into text.
    it is using speech_recognition library and recognize_google option to convert speech
    into text.
    """
    # def voice_cloud_processor(self, filename):
    #     """Transcribe the given audio file."""
    #     global recognized_text
    #     client = speech.SpeechClient()

    #     with io.open(filename, "rb") as audio_file:
    #         content = audio_file.read()

    #     audio = speech.RecognitionAudio(content=content)
    #     config = speech.RecognitionConfig(
    #         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    #         sample_rate_hertz=RESPEAKER_RATE,
    #         language_code=constants.Language,
    #         max_alternatives=1,
        
    #     )

    #     response = client.recognize(config=config, audio=audio)
    #     # Each result is for a consecutive portion of the audio. Iterate through
    #     # them to get the transcripts for the entire audio file.
    #     for result in response.results:
    #         # The first alternative is the most likely one for this portion.
    #         print(result.language_code)
    #         print(u"Transcript: {}".format(result.alternatives[0].transcript))
    #         recognized_text=result.alternatives[0].transcript
    #     os.remove(filename)
    #     return recognized_text  

    def voice_command_processor(self, filename):
        global recognized_text
        recognized_text=''
        with sr.AudioFile(filename) as source:
            #r.adjust_for_ambient_noise(source=source, duration=0.5)
          
            audio = Recognizer.record(source, duration=3)
            try:
                recognized_text = Recognizer.recognize_google(audio,language=constants.Language)
            except sr.UnknownValueError as e:
                pass
            except sr.RequestError as e:
                print("service is down")
                pass
        if recognized_text :print(recognized_text)
        os.remove(filename)
        return recognized_text





def main():
    """start bidirectional streaming from microphone input to speech API"""
    voice_obj = voice()    # Initializing the voice class.
    global recognized_text
    while True:
        file_name = voice_obj.process(3)
        voice_obj.voice_command_processor(file_name)
        if  re.search(r"\b(louis|لوي)\b", recognized_text, re.I) :
            print("wake word detected...")
            status = response.process_text(recognized_text,voice_obj,constants.Language)
            recognized_text = ''    
            time.sleep(0.2)
            command_file_name = voice_obj.process(5)
            voice_obj.voice_command_processor(command_file_name)
            print("you said :: " + recognized_text)
            status = response.process_text(recognized_text,voice_obj,constants.Language)
            while status != 'done':
                pass

            files = glob.glob(os.path.join(WAVE_OUTPUT_FILEPATH + '*.wav'))
            for file in files:
                os.remove(file)
            recognized_text = ''
       

if __name__ == "__main__":

    main()