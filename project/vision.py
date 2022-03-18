import html
# import picamera
import pygame
from google.cloud import texttospeech
import os
from google.cloud import vision
import io



# def takephoto():
#     camera = picamera.PiCamera()
#     camera.capture('image.jpg')

def textdetection():
    # takephoto() # First take a picture
    """Run a label request on a single image"""
    client = vision.ImageAnnotatorClient()

    with io.open('image.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    texts = response.text_annotations[0]
    print(texts.description)
    text_to_speech(texts.description)
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    
def objectdetection():
    # takephoto()
    client = vision.ImageAnnotatorClient()
    
    with io.open('image.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    objects = client.object_localization(
        image=image).localized_object_annotations
    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))


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
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.MALE
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
    with open("outfile.wav", "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file " + 'outfile.wav')
    os.system('mpg321 outfile.wav &')
    


if __name__ == '__main__':
    textdetection()


