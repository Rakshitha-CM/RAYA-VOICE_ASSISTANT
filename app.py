from flask import Flask, request, jsonify, send_from_directory
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import os
import subprocess
import shutil
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

email_data = {}

def create_engine():
    """Creates and returns a new pyttsx3 engine instance."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    engine.setProperty('voice', voices[1].id)  # Set to a female voice
    return engine

def talk(text):
    """Converts text to speech."""
    engine = create_engine()
    engine.say(text)
    engine.runAndWait()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Add a new variable to track the email state
email_state = {"step": None}  # Possible values: None, "email", "subject", "content"

@app.route('/api/command', methods=['POST'])
def handle_command():
    """Handle the command sent from the frontend."""
    global email_state
    data = request.json
    command = data.get('command', '').lower()
    response = ""

    print(f"Received command: {command}")  # Debug print
    print(f"Current email_data: {email_data}")  # Debug print
    print(f"Current email_state: {email_state}")  # Debug print

    try:
        if 'send email' in command:
            response = "Please provide the recipient's email address."
            email_data.clear()  # Clear any previous email data
            email_state["step"] = "email"
        elif email_state["step"] == "email":
            email_data['to'] = command.strip()
            response = "Please provide the email subject."
            email_state["step"] = "subject"
        elif email_state["step"] == "subject":
            email_data['subject'] = command.strip()
            response = "Please provide the email content."
            email_state["step"] = "content"
        elif email_state["step"] == "content":
            email_data['content'] = command.strip()
            if all(key in email_data for key in ['to', 'subject', 'content']):
                response = send_email(email_data['to'], email_data['subject'], email_data['content'])
                email_data.clear()  # Clear the email data after sending
                email_state["step"] = None  # Reset the state
            else:
                response = "Some email information is missing. Please start over with 'send email'."
        elif 'play' in command:
            song = command.replace('play', '').strip()
            response = f'Playing {song}'
            talk(response)
            pywhatkit.playonyt(song)
        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            response = f'Current time is {time}'
            talk(response)
        elif 'date' in command:
            today = datetime.datetime.now().strftime('%A, %B %d, %Y')
            response = f"Today's date is {today}"
            talk(response)
        elif 'who is' in command:
            person = command.replace('who is', '').strip()
            info = wikipedia.summary(person, sentences=1)
            response = info
            talk(response)
        elif 'what is' in command or 'when' in command or 'how' in command:
            query = command.replace('what is', '').strip()
            info = wikipedia.summary(query, sentences=1)
            response = info
            talk(response)
        elif 'what are you doing' in command:
            response = "I'm talking to my human friend."
            talk(response)
       
        elif "what's your name" in command:
            response = "My name is RAYA!."
            talk(response)
        elif 'tell me a joke' in command:
            response = pyjokes.get_joke()
            talk(response)
        elif 'open' in command:
            app_name = command.replace('open', '').strip()
            response = open_app(app_name)
        elif 'close' in command:
            app_name = command.replace('close', '').strip()
            response = close_app(app_name)
        elif 'hello' in command or 'hi' in command or 'hey' in command:
            response = "Hello! I'm RAYA. What can I do for you?"
            talk(response)
        elif 'bye' in command or 'goodbye' in command:
            response = "Bye!"
            talk(response)
        elif 'arrange files' in command:
            response = organize_files()
            talk(response)
        else:
            response = "I'm not sure how to respond to that."
            talk(response)

        print(f"Response: {response}")  # Debug print
        print(f"Updated email_data: {email_data}")  # Debug print

    except Exception as e:
        response = f"An error occurred: {str(e)}"

    return jsonify({'response': response})


def open_app(app_name):
    """Open an application or a website."""
    app_paths = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "notepad": "notepad",
        "pinterest": "https://in.pinterest.com/",
        "word": "Word",
        "ppt": "PowerPoint",
        "maps": "https://www.google.com/maps",
        "gmail": "https://mail.google.com",
        "whatsapp": "WhatsApp",
    }

    if app_name in app_paths:
        app_path = app_paths[app_name]
        if app_path.startswith("http"):
            webbrowser.open(app_path)
            return f'Opening {app_name}'
        else:
            subprocess.Popen(app_path)
            return f'Opening {app_name}'
    return f"Unknown application: {app_name}"

def close_app(app_name):
    """Close an application."""
    try:
        if app_name == "notepad":
            os.system("taskkill /IM notepad.exe /F")
        elif app_name == "chrome":
            os.system("taskkill /IM chrome.exe /F")
        else:
            os.system(f"taskkill /IM {app_name}.exe /F")
        return f"Closed {app_name} (if it was running)."
    except Exception as e:
        return f"Error closing {app_name}: {str(e)}"

def organize_files():
    desktop_path ="C:\\Users\\raksh\\OneDrive\\Desktop"
    year_folders = {
        '22': '2022',
        '23': '2023'
    }
    for year, folder in year_folders.items():
        folder_path = os.path.join(desktop_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    for file_name in os.listdir(desktop_path):
        file_path = os.path.join(desktop_path, file_name)
        if os.path.isfile(file_path):
            for year, folder in year_folders.items():
                if f"_{year}" in file_name:
                    target_folder = os.path.join(desktop_path, folder)
                    target_path = os.path.join(target_folder, file_name)
                    shutil.move(file_path, target_path)
                    print(f"Moved {file_name} to {folder}")
                    break
    return "Files organized successfully."

def send_email(receiver_email, subject, body):
    sender_email = "singhshubhangi3009@gmail.com"  # Replace with your email
    sender_password = "hazj lrph nltn ukcm"  # Replace with your app password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return f"Email successfully sent to {receiver_email}"
    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)