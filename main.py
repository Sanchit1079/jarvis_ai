import datetime
import os
import sys
import time
import webbrowser
import pyautogui
import pyttsx3
import speech_recognition as sr
import json
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import pickle  
import pyaudio  
import random
import numpy as np
import psutil

# Load intents, model, and tokenizer
with open("intents.json") as file:
    data = json.load(file)

model = load_model("chat_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder = pickle.load(encoder_file)

# Initialize text-to-speech engine
def initialize_engine():
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', engine.getProperty('rate') - 50)
    engine.setProperty('volume', engine.getProperty('volume') + 0.25)
    return engine

def speak(text):
    engine = initialize_engine()
    engine.say(text)
    engine.runAndWait()

def command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening.......", end="", flush=True)
        audio = r.listen(source)
    try:
        print("\rRecognizing......", end="", flush=True)
        query = r.recognize_google(audio, language='en-in')
        print(f"\rUser  said: {query}\n")
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return "None"
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return "None"
    return query.lower()

def cal_day():
    day = datetime.datetime.today().weekday() + 1
    day_dict = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    return day_dict.get(day, "Unknown")

def wishMe():
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M %p")
    day = cal_day()

    if hour < 12:
        speak(f"Good morning Sir, it's {day} and the time is {t}")
    elif hour < 17:
        speak(f"Good afternoon Sir, it's {day} and the time is {t}")
    else:
        speak(f"Good evening Sir, it's {day} and the time is {t}")

def social_media(command):
    platforms = {
        'facebook': "https://www.facebook.com/",
        'whatsapp': "https://web.whatsapp.com/",
        'discord': "https://discord.com/",
        'instagram': "https://www.instagram.com/",
    }
    for platform in platforms:
        if platform in command:
            speak(f"Opening your {platform}")
            webbrowser.open(platforms[platform])
            return
    speak("No result found")

def schedule():
    day = cal_day().lower()
    speak("Sir, today's schedule is:")
    week = {
        "monday": "Sir,from 9:00 to 9:50 you have Algorithms class...",
        "tuesday": "Sir, from 9:00 to 9:50 you have Web Development class...",
        "wednesday": "Sir, today you have a full day of classes...",
        "thursday": "Sir, today you have a full day of classes...",
        "friday": "Sir, today you have a half day of classes...",
        "saturday": "Sir, today you have a more relaxed day...",
        "sunday": "Sir, today is a holiday..."
    }
    speak(week.get(day, "No schedule found for today."))

def openApp(command):
    apps = {
        "calculator": 'C:\\Windows\\System32\\calc.exe',
        "notepad": 'C:\\Windows\\System32\\notepad.exe',
        "paint": 'C:\\Windows\\System32\\mspaint.exe',
    }
    for app in apps:
        if app in command:
            speak(f"Opening {app}")
            os.startfile(apps[app])
            return
    speak("No application found.")

def closeApp(command):
    apps = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
    }
    for app in apps:
        if app in command:
            speak(f"Closing {app}")
            os.system(f"taskkill /f /im {apps[app]}")
            return
    speak("No application found.")

def browsing(query):
    if 'google' in query:
        speak("Sir, what should I search on Google?")
        search_query = command()
        if search_query != "None":
            webbrowser.open(f"https://www.google.com/search?q={search_query}")

def condition():
    usage = str(psutil.cpu_percent())
    speak(f"CPU is at {usage} percentage")
    battery = psutil.sensors_battery()
    percentage = battery.percent
    speak(f"Sir, our system has {percentage} percentage battery.")

    if percentage >= 80:
        speak("we have enough charge to continue.")
    elif 40 <= percentage < 80:
        speak("And we should connect to a charging point.")
    else:
        speak("we have very low power, please connect to charging.")
        

if __name__ == "__main__":
    wishMe()
    while True:
        query = command()
        if "jarvis ruk jao" in query:
            speak("Goodbye Sir! Have a nice day, and i hope you like this project!")
            sys.exit()
            
        if query == "None":
            continue
        
        if any(platform in query for platform in ['facebook', 'discord', 'whatsapp', 'instagram']):
            social_media(query)
            
        elif "university time table" in query or "schedule" in query:
            schedule()
            
        elif "volume up" in query:
            pyautogui.press("volumeup")
            speak("Volume increased")
            
        elif "volume down" in query:
            pyautogui.press("volumedown")
            speak("Volume decreased")
            
        elif "mute" in query:
            pyautogui.press("volumemute")
            speak("Volume muted")
            
        elif any(app in query for app in ["calculator", "notepad", "paint"]):
            openApp(query)
            
        elif any(f"close {app}" in query for app in ["calculator", "notepad", "paint"]):
            closeApp(query)
            
        elif any(greeting in query for greeting in ["what", "who", "how", "hi", "thanks", "hello"]):
            padded_sequences = pad_sequences(tokenizer.texts_to_sequences([query]), maxlen=20, truncating='post')
            result = model.predict(padded_sequences)
            tag = label_encoder.inverse_transform([np.argmax(result)])
            for i in data['intents']:
                if i['tag'] == tag:
                    speak(random.choice(i['responses']))
                                 
        elif "open google" in query:
            browsing(query)
            
        elif "system condition" in query:
            speak("Checking the system condition...")
            condition()
            
        elif "exit" in query:
            speak("Goodbye Sir! Have a nice day and i hope sir, you like this project!")
            sys.exit()
        