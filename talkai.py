import streamlit as st
import pyttsx3
import speech_recognition as sr
from transformers import AutoModelForCausalLM, AutoTokenizer       
import time
import webbrowser
#from PIL import Image
import datetime
from streamlit_lottie import st_lottie
import requests

st.set_page_config(page_title = "Talk Ai", page_icon = "🤖")
st.sidebar.markdown("👇 Enter Your Name here to Continue")
name = st.sidebar.text_area("Enter Your Name:")
if name:
    st.sidebar.success(f"# Hello {name}!")
    st.sidebar.write("### Welcome To my Page")
    st.sidebar.write("## We are Introduced a Chatbot With Voice Activated ")
    st.sidebar.markdown("### How To Use:")
    st.sidebar.info("- Click the Start Button to Communicate with Talk AI ")
    st.sidebar.info("- Go to webiste with the help of keyword like -Open,Go to,Navigate to,Take me to")
    st.sidebar.info("- To Know the Current Time ")
    st.sidebar.info("- To know the Current Date ")
    st.sidebar.info("- Click the Stop Button to Exit TalkAi")
    
class Chatbot:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

    def get_response(self, user_input):
        with st.spinner("🤿 Chatbot processing response..."):
            input_ids = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors="pt")   
            bot_input = self.model.generate(
                input_ids,
                max_length=1000,
                pad_token_id=self.tokenizer.eos_token_id,   
                do_sample=True,
                top_k=50, 
                top_p=0.95,
                temperature=0.7
                )
            response = self.tokenizer.decode(bot_input[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
            return response

    @staticmethod
    def speak(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    @staticmethod
    def listen():
        recognizer = sr.Recognizer()
        with st.spinner("🎤 Listening for your input..."):
            with sr.Microphone() as source:
                time.sleep(1)
                try:
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio).lower()
                    return command
                except sr.UnknownValueError:
                    Chatbot.speak("Sorry, I couldn't understand that.")
                    return None
                except sr.RequestError:
                    Chatbot.speak("Error: Could not connect to the speech recognition server.")
                    return None

    def command_handler(self, command):
        if not command:
            return "No input received."
        phrases = ["open","go to","navigate to","take me to"]
        website = None
        for phrase in phrases:
            if phrase in command:
                website = command.replace(phrase, "").strip()
                break
        if website:
            Url = f"http://{website}.com" if "http" not in website else website
            try:
                webbrowser.open(Url)
                Chatbot.speak(f"Opening {website}")
                return f"Opening: {website}"
            except Exception:
                Chatbot.speak("Sorry, I could not open the website")
                return "Failed to open website"  
        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%H:%M")
            Chatbot.speak(f"Time is {current_time} ")       
            return f"Time is {current_time}"
        elif "date" in command:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            Chatbot.speak(f"Today's date is {current_date}")
            return f"Today's date is {current_date}"
        else:
            response = self.get_response(command)
            self.speak(response)
            return response

col1,col2,col3 = st.columns(3)
with col2:
    st.title(" Talk Ai")
def request(url):
    r = requests.get(url)  
    if r.status_code == 200:
        return r.json()
    else:
        return None  

value = request("https://lottie.host/35fd02d0-076c-444d-a2f5-59be0a2c38d7/wyoItYA3JX.json")    
if value:
    with col2:
        st_lottie(value,height=300)  
else:
    with col2:
        st.error("Failed to load animation")        

if "conversation" not in st.session_state:
    st.session_state["conversation"] = ""

if "listening" not in st.session_state:
    st.session_state["listening"] = False

chatbot = Chatbot()

# Display the conversation
conversation_placeholder = st.empty()

# Continuous listening function
def continuous_listening():
    while st.session_state["listening"]:
        user_input = chatbot.listen()
        if user_input:
            response = chatbot.command_handler(user_input)
            st.session_state["conversation"] += f"You: {user_input}\nBot: {response}\n"
            conversation_placeholder.text_area("Conversation", st.session_state["conversation"], height=300)
        time.sleep(1)  

# Start/Stop buttons
if st.button("Start"):
    st.session_state["listening"] = True

if st.button("Stop"):
    st.session_state["listening"] = False

# Handle continuous listening
if st.session_state["listening"]:
        continuous_listening()

   