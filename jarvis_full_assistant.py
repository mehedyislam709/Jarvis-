import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
from selenium import webdriver

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 

def speak(audio_text):
    print(f"Jarvis: {audio_text}")
    engine.say(audio_text)
    engine.runAndWait()

def greet_user():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Jarvis. How can I help you today?")

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Could not understand. Saying it again...")
        return "None"
    return query.lower()

def selenium_smooth_scroll(driver, scroll_duration=8):
    print("Jarvis: Beginning smooth browser scroll...")
    start_time = time.time()
    while time.time() - start_time < scroll_duration:
        driver.execute_script("window.scrollBy(0, 20);")
        time.sleep(0.05)
    print("Jarvis: Reached scroll limit.")

if __name__ == "__main__":
    # Initialize the browser driver for Selenium
    driver = webdriver.Chrome()
    driver.get("https://en.wikipedia.org/wiki/Python_(programming_language)")

    greet_user()
    
    while True:
        query = take_command()

        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                speak(results)
            except Exception:
                speak("I couldn't find any relevant details on Wikipedia.")

        elif 'open google' in query:
            speak("Opening Google.")
            webbrowser.open("google.com")

        elif 'open youtube' in query:
            speak("Opening YouTube.")
            webbrowser.open("youtube.com")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")    
            speak(f"Sir, the time is {strTime}")

        elif 'scroll down' in query:
            speak("Scrolling down, sir.")
            selenium_smooth_scroll(driver, scroll_duration=8)

        elif 'offline' in query or 'stop' in query or 'quit' in query:
            speak("Going offline. Goodbye, Sir!")
            driver.quit()
            break
