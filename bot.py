import inputs_outputs_it
import inputs_outputs_en
from tkinter import *
from PIL import Image, ImageTk
import pandas as pd
import speech_recognition
import threading
import pyttsx3
import random
import pyjokes
import AppOpener
import wikipedia
import pywhatkit
import requests
import time
from dotenv import load_dotenv
import os


def set_language():
    language_selection = input("Select language: It/En? ").lower()
    if language_selection == "it":
        user_lang = inputs_outputs_it
        return user_lang
    elif language_selection == "en":
        user_lang = inputs_outputs_en
        return user_lang
    else:
        print("Write 'It' or 'En'")
        set_language()


language = set_language()
print(language)

load_dotenv()

IMAGE_SLEEP = Image.open("images/sleep.png")
IMAGE_LISTEN = Image.open("images/listen.png")
IMAGE_TALK = Image.open("images/talk.png")
IMAGE_TIMER = Image.open("images/timer.png")
IMAGE_LOADING = Image.open("images/loading.png")


WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEOCODING_ENDPOINT = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"

wikipedia.set_user_agent('Voice-Assistant/1.1 (contact@example.com)')

if language == inputs_outputs_en:
    lang = "en"
    audio_lang = "en-EN"
    IMAGE_COMMANDS = Image.open("info/commands-en.png")
elif language == inputs_outputs_it:
    lang = "it"
    audio_lang = "it-IT"
    wikipedia.set_lang("it")
    IMAGE_COMMANDS = Image.open("info/commands-it.png")


class Bot:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300

        self.root = Tk()
        self.root.title("Bot")

        self.root.geometry("424x632")

        self.is_active = False
        self.start_timer = 0
        self.finish_timer = 0
        self.timer = 0
        self.timer_is_on = None

        self.is_talking = False

        self.image = ImageTk.PhotoImage(IMAGE_SLEEP)

        self.label = Label(self.root)
        self.label.pack(fill="both", expand=YES)
        self.label.config(image=self.image)

        threading.Thread(target=self.run, daemon=True).start()

        self.root.mainloop()

    def set_img_sleep(self):
        self.image = ImageTk.PhotoImage(IMAGE_SLEEP)
        self.label.config(image=self.image)

    def set_img_listen(self):
        self.image = ImageTk.PhotoImage(IMAGE_LISTEN)
        self.label.config(image=self.image)

    def set_img_talk(self):
        self.image = ImageTk.PhotoImage(IMAGE_TALK)
        self.label.config(image=self.image)

    def set_img_timer(self):
        self.image = ImageTk.PhotoImage(IMAGE_TIMER)
        self.label.config(image=self.image)

    def set_img_loading(self):
        self.image = ImageTk.PhotoImage(IMAGE_LOADING)
        self.label.config(image=self.image)

    def talk(self, speech, mood="normal"):
        self.wait_if_is_talking()

        self.is_talking = True
        if mood == "normal":
            self.set_img_talk()
        elif mood == "loading":
            self.set_img_loading()
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)
        if language == inputs_outputs_en:
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)
        engine.say(speech)
        engine.runAndWait()
        if mood == "normal":
            if self.is_active:
                self.set_img_listen()
            else:
                self.set_img_sleep()
        self.is_talking = False

    def check_timer(self):
        self.timer_is_on = True
        while self.timer_is_on:
            time.sleep(1)
            self.finish_timer = time.time()
            if self.finish_timer - self.start_timer >= self.timer:
                self.set_img_timer()
                self.talk(language.TIMER_FINISHED, mood="timer")
                self.timer = 0
                self.root.bind("<Return>", self.stop_timer)

    def stop_timer(self, event):
        self.timer_is_on = False
        if self.is_active:
            self.set_img_listen()
        else:
            self.set_img_sleep()

    def wait_if_is_talking(self):
        while self.is_talking:
            time.sleep(0.1)



    def run(self):
        while True:
            try:
                with speech_recognition.Microphone() as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                    audio = self.recognizer.listen(mic)
                    text = self.recognizer.recognize_google(audio, language=audio_lang)
                    text = text.lower()
                    print(text)

                    # Bot activates
                    if "ok" in text:
                        self.is_active = True

                        data = pd.read_csv("user-data.csv")
                        if data["name"][0] == "x":
                            answer = random.choice(language.BOT_GREETS).replace("user", "")
                            self.talk(answer)

                        else:
                            answer = random.choice(language.BOT_GREETS).replace("user", data["name"][0])
                            self.talk(answer)

                        while self.is_active:
                            try:
                                self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                                audio = self.recognizer.listen(mic)
                                text = self.recognizer.recognize_google(audio, language=audio_lang)
                                text = text.lower()
                                print(text)


                                # Get commands
                                if text == "info":
                                    self.talk(language.BOT_TELLS_INFO)
                                    IMAGE_COMMANDS.show()


                                # Set username
                                elif language.SET_USERNAME in text:
                                    try:
                                        split = text.split()
                                        if language == inputs_outputs_it:
                                            user_name_index = split.index("è") + 1
                                        elif language == inputs_outputs_en:
                                            user_name_index = split.index("is") + 1
                                        user_name = split[user_name_index]
                                        if user_name == "x":
                                            self.talk(language.NAME_REFUSED)
                                            continue
                                        self.talk(language.CONFIRM_NAME.replace("user", user_name))
                                        confirm = False

                                    except IndexError:
                                        self.talk(language.NOT_UNDERSTOOD)
                                        continue

                                    while not confirm:
                                        self.wait_if_is_talking()
                                        try:
                                            audio = self.recognizer.listen(mic)
                                            if self.is_talking:
                                                continue
                                            confirm_text = self.recognizer.recognize_google(audio, language=audio_lang)
                                            confirm_text = confirm_text.lower().split()
                                            print(confirm_text)

                                            if "sì" in confirm_text or "yes" in confirm_text or "yeah" in confirm_text:
                                                data.loc[0, "name"] = user_name
                                                data.to_csv("user-data.csv", index=False)

                                                self.talk(language.NAME_SAVED)
                                                confirm = True
                                                continue

                                            if "no" in confirm_text:
                                                self.talk(language.NAME_NOT_CONFIRMED)
                                                confirm = True

                                            else:
                                                self.talk(language.CONFIRM_NOT_UNDERSTOOD)


                                        except speech_recognition.UnknownValueError:
                                            self.talk(language.CONFIRM_NOT_UNDERSTOOD)



                                # Delete username
                                elif language.DELETE_NAME in text:
                                    data = pd.read_csv("user-data.csv")
                                    if data["name"][0] == "x":
                                        self.talk(language.NO_NAME_TO_DELETE)
                                    else:
                                        name_to_delete = data["name"][0]
                                        self.talk(language.CONFIRM_DELETE_NAME.replace("user", name_to_delete))

                                        confirm = False

                                        while not confirm:
                                            self.wait_if_is_talking()
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                if self.is_talking:
                                                    continue
                                                confirm_text = self.recognizer.recognize_google(audio, language=audio_lang)
                                                confirm_text = confirm_text.lower().split()
                                                print(confirm_text)

                                                self.wait_if_is_talking()

                                                if "sì" in confirm_text or "yes" in confirm_text or "yeah" in confirm_text:
                                                    data.loc[0, "name"] = "x"
                                                    data.to_csv("user-data.csv", index=False)

                                                    self.talk(language.NAME_DELETED)
                                                    confirm = True
                                                    continue

                                                if "no" in confirm_text:
                                                    self.talk(language.NAME_NOT_DELETED)
                                                    confirm = True

                                                else:
                                                    self.talk(language.CONFIRM_NOT_UNDERSTOOD)


                                            except speech_recognition.UnknownValueError:
                                                self.talk(language.CONFIRM_NOT_UNDERSTOOD)



                                elif any(user_input in text for user_input in language.USER_ASKS_WEATHER):
                                    if data["location"][0] == "x":
                                        self.talk(language.MISSING_LOCATION)
                                        location = False

                                        while not location:
                                            self.wait_if_is_talking()
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                if self.is_talking:
                                                    continue
                                                user_location = self.recognizer.recognize_google(audio, language=audio_lang)
                                                user_location = user_location.lower()
                                                print(f"location: {user_location}")

                                                self.wait_if_is_talking()

                                                if user_location == "x":
                                                    self.talk(language.INVALID_LOCATION)
                                                    continue

                                                geocoding_params = {
                                                    "q": user_location,
                                                    "appid": WEATHER_API_KEY,
                                                }

                                                response = requests.get(url=GEOCODING_ENDPOINT, params=geocoding_params)
                                                response.raise_for_status()
                                                try:
                                                    user_lat = response.json()[0]["lat"]
                                                    user_lon = response.json()[0]["lon"]
                                                    print(f"location:{user_location}\nlat: {user_lat}\nlon: {user_lon}")
                                                    data.loc[0, "location"] = user_location
                                                    data.loc[0, "lat"] = user_lat
                                                    data.loc[0, "lon"] = user_lon
                                                    data.to_csv("user-data.csv", index=False)
                                                    self.talk(language.LOCATION_CONFIRMED.replace("user_location", user_location))
                                                    location = True

                                                except IndexError:
                                                    self.talk(language.LOCATION_NOT_UNDERSTOOD)


                                            except speech_recognition.UnknownValueError:
                                                self.talk(language.NOT_UNDERSTOOD)


                                    else:
                                        user_location = data["location"][0]
                                        user_lat = data["lat"][0]
                                        user_lon = data["lon"][0]
                                        print(f"location:{user_location}\nlat: {user_lat}\nlon: {user_lon}")


                                    params = {
                                        "lat": user_lat,
                                        "lon": user_lon,
                                        "appid": WEATHER_API_KEY,
                                        "lang": lang,
                                        "units": "metric"
                                    }

                                    response = requests.get(WEATHER_FORECAST_ENDPOINT, params=params)
                                    response.raise_for_status()

                                    today_description = response.json()["list"][1]["weather"][0]["description"]
                                    today_temperature = response.json()["list"][1]["main"]["temp"]
                                    tomorrow_description = response.json()["list"][8]["weather"][0]["description"]
                                    tomorrow_temperature = response.json()["list"][8]["main"]["temp"]


                                    self.talk(language.WEATHER_FORECAST.replace("user_location", user_location).replace(
                                        "today_description", today_description).replace("today_temperature",str(today_temperature)).
                                              replace("tomorrow_description", tomorrow_description).replace(
                                        "tomorrow_temperature", str(tomorrow_temperature))
                                    )



                                # Change user location
                                elif language.CHANGE_LOCATION in text:
                                    self.talk(language.BOT_ASKS_LOCATION)
                                    location = False

                                    while not location:
                                        self.wait_if_is_talking()
                                        try:
                                            audio = self.recognizer.listen(mic)
                                            if self.is_talking:
                                                continue
                                            user_location = self.recognizer.recognize_google(audio, language=audio_lang)
                                            user_location = user_location.lower()
                                            print(f"location: {user_location}")

                                            self.wait_if_is_talking()

                                            if user_location == "x":
                                                self.talk(language.INVALID_LOCATION)
                                                continue

                                            geocoding_params = {
                                                "q": user_location,
                                                "appid": WEATHER_API_KEY,
                                            }

                                            response = requests.get(url=GEOCODING_ENDPOINT, params=geocoding_params)
                                            response.raise_for_status()
                                            try:
                                                user_lat = response.json()[0]["lat"]
                                                user_lon = response.json()[0]["lon"]
                                                print(f"lat: {user_lat}\nlon: {user_lon}")
                                                data.loc[0, "location"] = user_location
                                                data.loc[0, "lat"] = user_lat
                                                data.loc[0, "lon"] = user_lon
                                                data.to_csv("user-data.csv", index=False)
                                                self.talk(language.LOCATION_CONFIRMED)
                                                location = True

                                            except IndexError:
                                                self.talk(language.LOCATION_NOT_UNDERSTOOD)



                                        except speech_recognition.UnknownValueError:
                                            self.talk(language.NOT_UNDERSTOOD)



                                # Set timer
                                elif "timer" in text:
                                    seconds_timer = 0
                                    minutes_timer = 0

                                    if self.timer != 0:
                                        self.talk(language.TIMER_ALREADY_EXISTS)
                                        continue
                                    if language.SECONDS in text:
                                        seconds_index = text.split().index(language.SECONDS)
                                        seconds_timer = text.split()[seconds_index - 1]
                                        if seconds_timer == "un":
                                            seconds_timer = 1
                                        if language.MINUTES in text:
                                            minutes_index = text.split().index(language.MINUTES)
                                            minutes_timer = text.split()[minutes_index - 1]
                                        elif language.MINUTE in text:
                                            minutes_timer = 1


                                    elif language.MINUTES in text:
                                            minutes_index = text.split().index(language.MINUTES)
                                            minutes_timer = text.split()[minutes_index - 1]
                                            if language.SECOND in text:
                                                seconds_timer = 1

                                    elif language.MINUTE in text:
                                        minutes_timer = 1
                                        if language.SECONDS in text:
                                            seconds_index = text.split().index(language.SECONDS)
                                            seconds_timer = text.split()[seconds_index - 1]
                                        elif language.SECOND in text:
                                            seconds_timer = 1

                                    elif language.SECOND in text:
                                        seconds_timer = 1

                                    else:
                                        self.talk(language.TIMER_NOT_UNDERSTOOD)

                                    self.timer = int(minutes_timer) * 60 + int(seconds_timer)

                                    if self.timer == 0:
                                        self.talk(language.INVALID_TIMER)
                                        continue

                                    if minutes_timer == 1:
                                        if seconds_timer == 1:
                                            self.talk(language.ONE_MIN_ONE_SEC_TIMER)
                                        else:
                                            self.talk(language.ONE_MIN_TIMER.replace("seconds_timer", str(seconds_timer)))
                                    elif seconds_timer == 1:
                                        self.talk(language.ONE_SEC_TIMER.replace("minutes_timer", str(minutes_timer)))
                                    else:
                                        self.talk(language.SET_TIMER.replace("minutes_timer", str(minutes_timer)).
                                                  replace("seconds_timer", str(seconds_timer)))

                                    print(f"{minutes_timer} min, {seconds_timer} sec")


                                    print(f"{self.timer} total seconds")
                                    self.start_timer = time.time()
                                    threading.Thread(target=self.check_timer, daemon=True).start()





                                # Asking how is going
                                elif any(user_input in text for user_input in language.USER_ASKS_HOW_IS_GOING):
                                    answer = random.choice(language.BOT_ANSWERS_HOW_IS_GOING)
                                    self.talk(answer)


                                # Saying thank you
                                elif any(user_input in text for user_input in language.USER_THANKS):
                                    answer = random.choice(language.BOT_ANSWERS_THANKS)
                                    self.talk(answer)


                                # Handling complaints
                                elif any(user_input in text for user_input in language.USER_COMPLAINS):
                                    answer = random.choice(language.BOT_HANDLES_COMPLAINTS)
                                    self.talk(answer)


                                # Searching on wikipedia
                                elif any(user_input in text for user_input in language.USER_ASKS_TO_SEARCH):
                                    for user_input in language.USER_ASKS_TO_SEARCH:
                                        if user_input in text:
                                            query = text.replace(user_input, "").strip()


                                    speech = language.BOT_SEARCHES_INFO.replace("query", query)
                                    self.talk(speech, mood="loading")
                                    try:
                                        search_result = wikipedia.summary(query, sentences=1)
                                        print(search_result)
                                        self.talk(language.SEARCH_RESULT + search_result)
                                    except wikipedia.exceptions.PageError:
                                        self.talk(language.NO_SEARCH_RESULTS)
                                    except wikipedia.exceptions.DisambiguationError:
                                        answer = language.DISAMBIGUATION_ERROR.replace("query", query)
                                        self.talk(answer)
                                    except requests.exceptions.JSONDecodeError:
                                        self.talk(language.ERROR_DURING_RESEARCH)
                                    except wikipedia.exceptions.WikipediaException:
                                        self.talk(language.ERROR_DURING_RESEARCH)



                                elif any(user_input in text for user_input in language.USER_SEARCHES_ON_YT):
                                    query = text
                                    for words in language.USER_SEARCHES_ON_YT:
                                        if words in query:
                                            query = query.replace(words, "").strip()

                                    self.talk(language.BOT_PLAYS_VIDEO.replace("query", query))
                                    print(f"search on youtube: {query}")
                                    pywhatkit.playonyt(query)



                                # Opens WhatsApp
                                elif language.OPEN_WHATSAPP in text:
                                    self.talk(language.BOT_OPENS_WHATSAPP)
                                    AppOpener.open("whatsapp")



                                # Opens Google
                                elif language.OPEN_GOOGLE in text:
                                    self.talk(language.BOT_OPENS_GOOGLE)
                                    AppOpener.open("google chrome")



                                # Tells a joke
                                elif any(user_input in text for user_input in language.ASK_JOKE):
                                    joke = pyjokes.get_joke(language=lang, category="all")
                                    print(f"joke: {joke}")
                                    self.talk(joke)


                                # Bot goes to sleep
                                elif language.SEND_BOT_TO_SLEEP in text:
                                    answer = random.choice(language.BOT_GOES_TO_SLEEP)
                                    self.talk(answer)

                                    self.set_img_sleep()
                                    self.is_active = False


                                elif text is not None:
                                    self.talk(language.NOT_UNDERSTOOD)
                                    continue

                                else:
                                    continue

                            except speech_recognition.UnknownValueError:
                                continue

            except speech_recognition.UnknownValueError:
                continue






bot = Bot()