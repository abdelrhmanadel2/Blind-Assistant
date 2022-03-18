"""
This file process converted text and perform actions accordingly.
This file can be extended with more action.
"""
from fileinput import filename
import random as rand
import constants
import speak 
import actions 
import time
import logging
import re
import json
logger = logging.getLogger('voice assistant')
# Opening JSON file
f = open('project/responses.json',encoding="utf-8")
 
# returns JSON object as
# a dictionary
response_phrase = json.load(f)
f.close()

def process_text(text, voice_object,language):
    altrinatives=response_phrase[language]
    """

    asking who are you?
    """
    if  re.search(r"\b(لوي|louis)\b", text, re.I) :
        # speak.audio_playback("i am a i voice assistant system")
        # time.sleep(0.5)
        greeting=altrinatives["greeting"]
        # print(random.randint(0,len(greeting)-1))
        greet = greeting[rand.randint(0,len(greeting)-1)]+constants.username
        speak.audio_playback(greet)

    """
    asking about weather information.
    """
    if re.search(r"\b(weather|الطقس)\b", text, re.I):
        report=altrinatives["weather"]
        speak.audio_playback(report["ask_city"])
        time.sleep(0.5)
        file_name = voice_object.process(5)
        city = voice_object.voice_command_processor(file_name)
        logger.info("process_text : City :: " + city)
        try:
            humidity, temp, phrase = actions.weatherReport(city,language)
            print(report["response"])
            fulltext=report["response"].format(city=city,temp=temp,humidity=humidity ,phrase=phrase)
            speak.audio_playback(fulltext)
         
        except KeyError as e:
            speak.audio_playback(report["error"])

            
    """
    asking for search somthing like:
    what is raspberry pi
    who is isac newton etc.
    """
    if re.search(r"\b(read this|اقرا النص|اقرا|أقراء)\b", text, re.I):
        report=altrinatives["textdetection"]
        speak.audio_playback(report["response"] )
        time.sleep(0.5)
        try:
            result =  actions.textdetection()
            result = actions.translate_text(language,result)
            if result:
                speak.audio_playback(result)
        
        except KeyError as e:
            speak.audio_playback(report["error"])
            pass
    if re.search(r"\b(explore|explores|Explore|what are there|استكشف|أستكشف)\b", text, re.I):
        report=altrinatives["objectdetection"]
        speak.audio_playback(report["response"] )
        time.sleep(0.5)
        try:
            result =  actions.objectdetection()
            result = actions.translate_text(result,language)
            print(result)
            if result:
                speak.audio_playback(result)
        
        except KeyError as e:
            speak.audio_playback(report["error"])
            pass

        
    """
    asking aboout current time.
    """
    if re.search(r"\b(time|Time|الساعه|الوقت)\b", text, re.I):
        report=altrinatives["time"]
        current_time = actions.current_datetime("time")
        speak.audio_playback(report["response"] + current_time)

    """
    asking about today's date.
    """
    if  re.search(r"\b(date|Date|تاريخ اليوم|التاريخ)\b", text, re.I):
        date = actions.current_datetime("date")
        report=altrinatives["date"]
        speak.audio_playback(report["response"] + date)
    
    
    if re.search(r"\b(change language|تغيير اللغه|switch language)\b", text, re.I):
        current_language = actions.change_language(language) 
        altrinatives=response_phrase[current_language]
        report=altrinatives["change-language"]
        speak.audio_playback(report["response"] + report["language-name"])
    
    if re.search(r"\b(change username|تغيير الأسم)\b", text, re.I):
        report=altrinatives["change-name"]
        speak.audio_playback(report["ask"])
        time.sleep(0.5)
        file_name = voice_object.process(3)
        user_name = voice_object.voice_command_processor(file_name)
        current_name = actions.change_username(user_name) 
        speak.audio_playback(report["response"] + current_name)
       
    """
    asking for rebooting the voice assistant system.
    """
    if "reboot" in text or "Reboot" in text:
        speak.audio_playback("ok.. rebooting the server")
        actions.reboot_server()

    return "done"
