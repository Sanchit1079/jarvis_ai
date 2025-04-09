from flask import Flask, render_template, request, jsonify
import datetime
import random
import json
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import psutil
import webbrowser
import os
import threading
import sys

app = Flask(__name__)

# Load intents, model, and tokenizer
with open("intents.json") as file:
    data = json.load(file)

model = load_model("chat_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder = pickle.load(encoder_file)

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

def get_time_greeting():
    hour = int(datetime.datetime.now().hour)
    t = datetime.datetime.now().strftime("%I:%M %p")
    day = cal_day()

    if hour < 12:
        return f"Good morning, it's {day} and the time is {t}"
    elif hour < 17:
        return f"Good afternoon, it's {day} and the time is {t}"
    else:
        return f"Good evening, it's {day} and the time is {t}"

def get_system_condition():
    usage = str(psutil.cpu_percent())
    battery = psutil.sensors_battery()
    percentage = battery.percent if battery else "Unknown"
    
    response = f"CPU is at {usage} percentage. "
    
    if battery:
        response += f"System has {percentage} percentage battery. "
        if percentage >= 80:
            response += "We have enough charge to continue."
        elif 40 <= percentage < 80:
            response += "We should connect to a charging point."
        else:
            response += "We have very low power, please connect to charging."
    
    return response

def schedule():
    day = cal_day().lower()
    week = {
        "monday": "From 9:00 to 9:50 you have Algorithms class...",
        "tuesday": "From 9:00 to 9:50 you have Web Development class...",
        "wednesday": "Today you have a full day of classes...",
        "thursday": "Today you have a full day of classes...",
        "friday": "Today you have a half day of classes...",
        "saturday": "Today you have a more relaxed day...",
        "sunday": "Today is a holiday..."
    }
    return week.get(day, "No schedule found for today.")

def open_browser(url):
    """Open a browser window in a separate thread"""
    def _open_browser():
        webbrowser.open(url)
    thread = threading.Thread(target=_open_browser)
    thread.start()
    return "Opening " + url

def open_application(app_name):
    """Open a desktop application in a separate thread"""
    apps = {
        "calculator": 'C:\\Windows\\System32\\calc.exe',
        "notepad": 'C:\\Windows\\System32\\notepad.exe',
        "paint": 'C:\\Windows\\System32\\mspaint.exe',
    }
    
    if app_name.lower() in apps:
        def _open_app():
            os.startfile(apps[app_name.lower()])
        thread = threading.Thread(target=_open_app)
        thread.start()
        return f"Opening {app_name}"
    return f"Sorry, I don't know how to open {app_name}"

def close_application(app_name):
    """Close a desktop application"""
    apps = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
    }
    
    if app_name.lower() in apps:
        try:
            os.system(f"taskkill /f /im {apps[app_name.lower()]}")
            return f"Closed {app_name}"
        except:
            return f"Failed to close {app_name}"
    return f"Sorry, I don't know how to close {app_name}"

def social_media(command):
    platforms = {
        'facebook': "https://www.facebook.com/",
        'whatsapp': "https://web.whatsapp.com/",
        'discord': "https://discord.com/",
        'instagram': "https://www.instagram.com/",
    }
    
    for platform in platforms:
        if platform in command:
            return open_browser(platforms[platform])
    
    return "No social media platform specified"

def process_query(query):
    query = query.lower()
    
    # Process system-related commands first
    if "system condition" in query:
        return get_system_condition()
    
    if "university time table" in query or "schedule" in query:
        return schedule()
    
    if "datetime" in query or "what is the time" in query or "what is the date" in query:
        return get_time_greeting()
    
    # Web browsing commands
    if "open google" in query:
        if "search" in query:
            search_term = query.split("search")[-1].strip()
            url = f"https://www.google.com/search?q={search_term}"
        else:
            url = "https://www.google.com"
        return open_browser(url)
    
    # Social media commands
    if any(platform in query for platform in ['facebook', 'discord', 'whatsapp', 'instagram']):
        return social_media(query)
    
    # Application commands
    if "open" in query:
        for app in ["calculator", "notepad", "paint"]:
            if app in query:
                return open_application(app)
    
    if "close" in query:
        for app in ["calculator", "notepad", "paint"]:
            if app in query:
                return close_application(app)
    
    # Use the model to predict intent
    padded_sequences = pad_sequences(tokenizer.texts_to_sequences([query]), maxlen=20, truncating='post')
    result = model.predict(padded_sequences)
    tag = label_encoder.inverse_transform([np.argmax(result)])[0]
    
    for i in data['intents']:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    
    return "I'm not sure how to respond to that."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json['message']
    response = process_query(user_message)
    return jsonify({'response': response})

@app.route('/get_initial_greeting')
def get_initial_greeting():
    return jsonify({'greeting': get_time_greeting()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)