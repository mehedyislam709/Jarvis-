import speech_recognition as sr.
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Set the assistant voice (usually voices[0] is male, voices[1] is female)
engine.setProperty('voice', voices[0].id) 

def speak(audio_text):
    """Pronounces the given text."""
    print(f"Jarvis: {audio_text}")
    engine.say(audio_text)
    engine.runAndWait()

def greet_user():
    """Greets the user based on the time of day."""
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    
    speak("I am Jarvis. How can I help you today?")

def take_command():
    """Listens to the microphone and returns recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1  # Wait time before ending phrase capture
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

if __name__ == "__main__":
    greet_user()
    
    while True:
        query = take_command()

        # Logic for executing tasks based on query
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

        elif 'open code' in query:
            # Change this path to where your VS Code or target program is installed
            code_path = "C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            if os.path.exists(code_path):
                speak("Opening VS Code.")
                os.startfile(code_path)
            else:
                speak("Visual Studio Code path is incorrect. Please update the script.")

        elif 'offline' in query or 'stop' in query or 'quit' in query:
            speak("Going offline. Goodbye, Sir!")
            break

