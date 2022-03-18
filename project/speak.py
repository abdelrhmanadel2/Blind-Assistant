import constants
import os
import html
from google.cloud import texttospeech
from playsound import playsound
AUDIO_PLAYBACK_FILENAME = "ramdisk/audio_play_back.mp3"

def audio_playback(text):
    text_to_speech(text)
    playsound(AUDIO_PLAYBACK_FILENAME)
    os.remove(AUDIO_PLAYBACK_FILENAME)
def text_to_speech(text):
    """Converts plaintext to SSML and
    generates synthetic audio from SSML

    ARGS
    text: text to synthesize
    outfile: filename to use to store synthetic audio

    RETURNS
    nothing
    """
    
    # Replace special characters with HTML Ampersand Character Codes
    # These Codes prevent the API from confusing text with
    # SSML commands
    # For example, '<' --> '&lt;' and '&' --> '&amp;'
    escaped_lines = html.escape(text)

    # Convert plaintext to SSML in order to wait two seconds
    #   between each line in synthetic speech
    ssml = "<speak>{}</speak>".format(
        escaped_lines.replace("\n", '\n<break time="2s"/>')
    )

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Sets the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

    # Builds the voice request, selects the language code ("en-US") and
    # the SSML voice gender ("MALE")
    voice = texttospeech.VoiceSelectionParams(
        language_code=constants.Language, ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    # Selects the type of audio file to return
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Performs the text-to-speech request on the text input with the selected
    # voice parameters and audio file type

    request = texttospeech.SynthesizeSpeechRequest(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    response = client.synthesize_speech(request=request)
    
    # Writes the synthetic audio to the output file.
    with open(AUDIO_PLAYBACK_FILENAME, "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file " + AUDIO_PLAYBACK_FILENAME)
    os.system('mpg321 ${AUDIO_PLAYBACK_FILENAME} &')

