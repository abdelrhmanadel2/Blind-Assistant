import weathercom
import json
from bs4 import BeautifulSoup
import requests
from googletrans import Translator
import urllib.request
import subprocess
import logging
import os
from google.cloud import vision
import io
import constants


logger = logging.getLogger('voice assistant')

"""
Getting weather report from weather.com
"""
def weatherReport(city,language): 
    weather_language={"en-us":"en-US","ar-eg":"ar-EG"}
    language_code=weather_language[language]
    weatherDetails = weathercom.getCityWeatherDetails(language_code,city) 
    humidity =json.loads(weatherDetails)["vt1observation"]["humidity"] 
    temp = json.loads(weatherDetails)["vt1observation"]["temperature"] 
    phrase = json.loads(weatherDetails)["vt1observation"]["phrase"]
    return humidity, temp, phrase



"""
get the current date and time.
"""
def current_datetime(type):
    
    returndata = ''
    timeData = urllib.request.urlopen("http://worldtimeapi.org/api/ip").read()
    datetime = json.loads(timeData)["datetime"]
    date = datetime.split("T")[0]
    time = datetime.split("T")[1]
    
    if type == "time":    
        time = time.split(".")[0]
    
        hr = int(time.split(":")[0])
        min = time.split(":")[1]
        suffix = ''
        if hr >12:
            hr = hr - 12
            suffix="PM"
        else:
            suffix="AM"
    
        if hr == 0:
            hr=12
            suffix="AM"
    
        final_time = str(hr)+":"+min+" "+suffix
        logger.info("current_datetime : current time : "+final_time)
        returndata = final_time
    
    if type == "date":
        year = date.split("-")[0]
        month_int=int(date.split("-")[1])
        day = date.split("-")[2]
    
        month = ''
    
        if month_int == 1:
            month = 'Janiary'
        elif  month_int == 2:
            month = "February"
        elif month_int == 3:
            month = "March"
        elif month_int == 4:
            month = "April"
        elif month_int == 5:
            month = "May"
        elif month_int == 6:
            month = "June"
        elif month_int == 7:
            month = "July"
        elif month_int == 8:
            month = "August"
        elif month_int == 9:
            month = "September"
        elif month_int == 10:
            month = "October"
        elif month_int == 11:
            month = "Novenber"
        elif month_int == 12:
            month = "December"
        
        logger.info("current_datetime : today's date : "+month+" " +day+", "+year)
        returndata = month+" " +day+", "+year
    
    return returndata


def textdetection():
    # takephoto() # First take a picture
    """Run a label request on a single image"""
    client = vision.ImageAnnotatorClient()

    with io.open('ramdisk\image3.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    else:
        texts = response.text_annotations[0].description
        print(texts.replace("\n",""))
        return texts.replace("\n","")
    
def objectdetection():
    # takephoto()
    client = vision.ImageAnnotatorClient()
    result=""
    with io.open('ramdisk\objectdetection.jpeg', 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    objects = client.object_localization(
        image=image).localized_object_annotations
    print('Number of objects found: {}'.format(len(objects)))
    i=1
    for object_ in objects:
        result+='\n object{}- {} (confidence: {})'.format(i,object_.name,str( object_.score)[0:3:1])
        i+=1
        print('\n{} (confidence: {})'.format(object_.name, str( object_.score)[0:3:1]))

    print(result)    
    return result   

def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target[0:2])

    print(u"Text: {}".format(result["input"]))
    print(u"Translation: {}".format(result["translatedText"]))
    print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result["translatedText"]

def change_language(language):
    if language=="en-us":
        constants.Language="ar-eg"
    else:
        constants.Language="en-us"   
    return constants.Language 
def change_username(name):
    constants.username=name
    return constants.username           
"""
Reboot raspberry pi.
"""
def reboot_server():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

