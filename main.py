import inputs_outputs_it
import inputs_outputs_en
from tkinter import *
from tkinter import ttk
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


class Bot:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300

        self.language = inputs_outputs_en
        self.lang = "en"
        self.audio_lang = "en-EN"
        wikipedia.set_lang("en")
        self.IMAGE_COMMANDS = Image.open("info/commands-en.png")

        self.root = Tk()
        self.root.title("Bot")

        self.root.geometry("424x632")

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)

        self.is_active = False
        self.start_timer = 0
        self.finish_timer = 0
        self.timer = 0
        self.timer_is_on = None

        self.is_talking = False
        print(self.language.START_INPUT)

        self.image = ImageTk.PhotoImage(IMAGE_SLEEP)

        data = pd.read_csv("user-data.csv")
        self.set_language(data["language"][0],data)

        self.canva = Canvas(self.root)
        self.bg_image = self.canva.create_image(0, 0, image=self.image, anchor="nw")
        self.canva.pack(fill="both", expand=YES)

        self.n = StringVar()
        self.lang_choice = ttk.Combobox(self.root, textvariable=self.n, width=15, state="readonly")
        self.lang_choice["values"] = ("English", "Italiano")
        self.lang_choice.set(data["language"][0])
        self.canva.create_window(10, 10, anchor="nw", window=self.lang_choice)
        self.lang_choice.bind("<<ComboboxSelected>>", self.on_language_selected)


        threading.Thread(target=self.run, daemon=True).start()

        self.root.mainloop()

    def on_language_selected(self, event):
        data = pd.read_csv("user-data.csv")
        new_lang = self.lang_choice.get()
        self.set_language(new_lang, data)

    def set_language(self, lng, csv):
        if lng == "English":
            self.language = inputs_outputs_en
            self.lang = "en"
            self.audio_lang = "en-EN"
            wikipedia.set_lang("en")
            self.IMAGE_COMMANDS = Image.open("info/commands-en.png")
        elif lng == "Italiano":
            self.language = inputs_outputs_it
            self.lang = "it"
            self.audio_lang = "it-IT"
            wikipedia.set_lang("it")
            self.IMAGE_COMMANDS = Image.open("info/commands-it.png")

        csv.loc[0, "language"] = lng
        csv.to_csv("user-data.csv", index=False)
        if self.is_active:
            self.talk(self.language.CHANGED_LANGUAGE)

    def lock_ui(self):
        self.lang_choice.config(state="disabled")

    def unlock_ui(self):
        self.lang_choice.config(state="readonly")


    def set_img_sleep(self):
        self.image = ImageTk.PhotoImage(IMAGE_SLEEP)
        self.canva.itemconfig(self.bg_image, image=self.image)

    def set_img_listen(self):
        self.image = ImageTk.PhotoImage(IMAGE_LISTEN)
        self.canva.itemconfig(self.bg_image, image=self.image)

    def set_img_talk(self):
        self.image = ImageTk.PhotoImage(IMAGE_TALK)
        self.canva.itemconfig(self.bg_image, image=self.image)

    def set_img_timer(self):
        self.image = ImageTk.PhotoImage(IMAGE_TIMER)
        self.canva.itemconfig(self.bg_image, image=self.image)

    def set_img_loading(self):
        self.image = ImageTk.PhotoImage(IMAGE_LOADING)
        self.canva.itemconfig(self.bg_image, image=self.image)

    def talk(self, speech, mood="normal"):
        self.lock_ui()
        self.wait_if_is_talking()

        self.is_talking = True
        if mood == "normal":
            self.set_img_talk()
        elif mood == "loading":
            self.set_img_loading()
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)
        if self.language == inputs_outputs_en:
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
        self.unlock_ui()

    def check_timer(self):
        self.timer_is_on = True
        while self.timer_is_on:
            time.sleep(1)
            self.finish_timer = time.time()
            if self.finish_timer - self.start_timer >= self.timer:
                self.set_img_timer()
                self.talk(self.language.TIMER_FINISHED, mood="timer")
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
                    text = self.recognizer.recognize_google(audio, language=self.audio_lang)
                    text = text.lower()
                    print(text)

                    # Bot activates
                    if "ok" in text:
                        self.is_active = True

                        data = pd.read_csv("user-data.csv")
                        if data["name"][0] == "x":
                            answer = random.choice(self.language.BOT_GREETS).replace("user", "")
                            self.talk(answer)

                        else:
                            answer = random.choice(self.language.BOT_GREETS).replace("user", data["name"][0])
                            self.talk(answer)

                        while self.is_active:
                            try:
                                self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                                audio = self.recognizer.listen(mic)
                                text = self.recognizer.recognize_google(audio, language=self.audio_lang)
                                text = text.lower()
                                print(text)


                                # Get commands
                                if text == "info":
                                    self.talk(self.language.BOT_TELLS_INFO)
                                    self.IMAGE_COMMANDS.show()


                                # Set username
                                elif self.language.SET_USERNAME in text:
                                    try:
                                        split = text.split()
                                        if self.language == inputs_outputs_it:
                                            user_name_index = split.index("è") + 1
                                        elif self.language == inputs_outputs_en:
                                            user_name_index = split.index("is") + 1
                                        user_name = split[user_name_index]
                                        if user_name == "x":
                                            self.talk(self.language.NAME_REFUSED)
                                            continue
                                        self.talk(self.language.CONFIRM_NAME.replace("user", user_name))
                                        confirm = False

                                    except IndexError:
                                        self.talk(self.language.NOT_UNDERSTOOD)
                                        continue

                                    while not confirm:
                                        self.wait_if_is_talking()
                                        try:
                                            audio = self.recognizer.listen(mic)
                                            if self.is_talking:
                                                continue
                                            confirm_text = self.recognizer.recognize_google(audio, language=self.audio_lang)
                                            confirm_text = confirm_text.lower().split()
                                            print(confirm_text)

                                            if "sì" in confirm_text or "yes" in confirm_text or "yeah" in confirm_text:
                                                data.loc[0, "name"] = user_name
                                                data.to_csv("user-data.csv", index=False)

                                                self.talk(self.language.NAME_SAVED)
                                                confirm = True
                                                continue

                                            if "no" in confirm_text:
                                                self.talk(self.language.NAME_NOT_CONFIRMED)
                                                confirm = True

                                            else:
                                                self.talk(self.language.CONFIRM_NOT_UNDERSTOOD)


                                        except speech_recognition.UnknownValueError:
                                            self.talk(self.language.CONFIRM_NOT_UNDERSTOOD)



                                # Delete username
                                elif self.language.DELETE_NAME in text:
                                    data = pd.read_csv("user-data.csv")
                                    if data["name"][0] == "x":
                                        self.talk(self.language.NO_NAME_TO_DELETE)
                                    else:
                                        name_to_delete = data["name"][0]
                                        self.talk(self.language.CONFIRM_DELETE_NAME.replace("user", name_to_delete))

                                        confirm = False

                                        while not confirm:
                                            self.wait_if_is_talking()
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                if self.is_talking:
                                                    continue
                                                confirm_text = self.recognizer.recognize_google(audio, language=self.audio_lang)
                                                confirm_text = confirm_text.lower().split()
                                                print(confirm_text)

                                                self.wait_if_is_talking()

                                                if "sì" in confirm_text or "yes" in confirm_text or "yeah" in confirm_text:
                                                    data.loc[0, "name"] = "x"
                                                    data.to_csv("user-data.csv", index=False)

                                                    self.talk(self.language.NAME_DELETED)
                                                    confirm = True
                                                    continue

                                                if "no" in confirm_text:
                                                    self.talk(self.language.NAME_NOT_DELETED)
                                                    confirm = True

                                                else:
                                                    self.talk(self.language.CONFIRM_NOT_UNDERSTOOD)


                                            except speech_recognition.UnknownValueError:
                                                self.talk(self.language.CONFIRM_NOT_UNDERSTOOD)



                                elif any(user_input in text for user_input in self.language.USER_ASKS_WEATHER):
                                    if data["location"][0] == "x":
                                        self.talk(self.language.MISSING_LOCATION)
                                        location = False

                                        while not location:
                                            self.wait_if_is_talking()
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                if self.is_talking:
                                                    continue
                                                user_location = self.recognizer.recognize_google(audio, language=self.audio_lang)
                                                user_location = user_location.lower()
                                                print(f"location: {user_location}")

                                                self.wait_if_is_talking()

                                                if user_location == "x":
                                                    self.talk(self.language.INVALID_LOCATION)
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
                                                    self.talk(self.language.LOCATION_CONFIRMED.replace("user_location", user_location))
                                                    location = True

                                                except IndexError:
                                                    self.talk(self.language.LOCATION_NOT_UNDERSTOOD)


                                            except speech_recognition.UnknownValueError:
                                                self.talk(self.language.NOT_UNDERSTOOD)


                                    else:
                                        user_location = data["location"][0]
                                        user_lat = data["lat"][0]
                                        user_lon = data["lon"][0]
                                        print(f"location:{user_location}\nlat: {user_lat}\nlon: {user_lon}")


                                    params = {
                                        "lat": user_lat,
                                        "lon": user_lon,
                                        "appid": WEATHER_API_KEY,
                                        "lang": self.lang,
                                        "units": "metric"
                                    }

                                    response = requests.get(WEATHER_FORECAST_ENDPOINT, params=params)
                                    response.raise_for_status()

                                    today_description = response.json()["list"][1]["weather"][0]["description"]
                                    today_temperature = response.json()["list"][1]["main"]["temp"]
                                    tomorrow_description = response.json()["list"][8]["weather"][0]["description"]
                                    tomorrow_temperature = response.json()["list"][8]["main"]["temp"]


                                    self.talk(self.language.WEATHER_FORECAST.replace("user_location", user_location).replace(
                                        "today_description", today_description).replace("today_temperature",str(today_temperature)).
                                              replace("tomorrow_description", tomorrow_description).replace(
                                        "tomorrow_temperature", str(tomorrow_temperature))
                                    )



                                # Change user location
                                elif self.language.CHANGE_LOCATION in text:
                                    self.talk(self.language.BOT_ASKS_LOCATION)
                                    location = False

                                    while not location:
                                        self.wait_if_is_talking()
                                        try:
                                            audio = self.recognizer.listen(mic)
                                            if self.is_talking:
                                                continue
                                            user_location = self.recognizer.recognize_google(audio, language=self.audio_lang)
                                            user_location = user_location.lower()
                                            print(f"location: {user_location}")

                                            self.wait_if_is_talking()

                                            if user_location == "x":
                                                self.talk(self.language.INVALID_LOCATION)
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
                                                self.talk(self.language.LOCATION_CONFIRMED.replace("user_location", user_location))
                                                location = True

                                            except IndexError:
                                                self.talk(self.language.LOCATION_NOT_UNDERSTOOD)



                                        except speech_recognition.UnknownValueError:
                                            self.talk(self.language.NOT_UNDERSTOOD)



                                # Set timer
                                elif "timer" in text:
                                    seconds_timer = 0
                                    minutes_timer = 0

                                    if self.timer != 0:
                                        self.talk(self.language.TIMER_ALREADY_EXISTS)
                                        continue
                                    if self.language.SECONDS in text:
                                        seconds_index = text.split().index(self.language.SECONDS)
                                        seconds_timer = text.split()[seconds_index - 1]
                                        if seconds_timer == "un":
                                            seconds_timer = 1
                                        if self.language.MINUTES in text:
                                            minutes_index = text.split().index(self.language.MINUTES)
                                            minutes_timer = text.split()[minutes_index - 1]
                                        elif self.language.MINUTE in text:
                                            minutes_timer = 1


                                    elif self.language.MINUTES in text:
                                            minutes_index = text.split().index(self.language.MINUTES)
                                            minutes_timer = text.split()[minutes_index - 1]
                                            if self.language.SECOND in text:
                                                seconds_timer = 1

                                    elif self.language.MINUTE in text:
                                        minutes_timer = 1
                                        if self.language.SECONDS in text:
                                            seconds_index = text.split().index(self.language.SECONDS)
                                            seconds_timer = text.split()[seconds_index - 1]
                                        elif self.language.SECOND in text:
                                            seconds_timer = 1

                                    elif self.language.SECOND in text:
                                        seconds_timer = 1

                                    else:
                                        self.talk(self.language.TIMER_NOT_UNDERSTOOD)

                                    self.timer = int(minutes_timer) * 60 + int(seconds_timer)

                                    if self.timer == 0:
                                        self.talk(self.language.INVALID_TIMER)
                                        continue

                                    if minutes_timer == 1:
                                        if seconds_timer == 1:
                                            self.talk(self.language.ONE_MIN_ONE_SEC_TIMER)
                                        else:
                                            self.talk(self.language.ONE_MIN_TIMER.replace("seconds_timer", str(seconds_timer)))
                                    elif seconds_timer == 1:
                                        self.talk(self.language.ONE_SEC_TIMER.replace("minutes_timer", str(minutes_timer)))
                                    else:
                                        self.talk(self.language.SET_TIMER.replace("minutes_timer", str(minutes_timer)).
                                                  replace("seconds_timer", str(seconds_timer)))

                                    print(f"{minutes_timer} min, {seconds_timer} sec")


                                    print(f"{self.timer} total seconds")
                                    self.start_timer = time.time()
                                    threading.Thread(target=self.check_timer, daemon=True).start()





                                # Asking how is going
                                elif any(user_input in text for user_input in self.language.USER_ASKS_HOW_IS_GOING):
                                    answer = random.choice(self.language.BOT_ANSWERS_HOW_IS_GOING)
                                    self.talk(answer)


                                # Saying thank you
                                elif any(user_input in text for user_input in self.language.USER_THANKS):
                                    answer = random.choice(self.language.BOT_ANSWERS_THANKS)
                                    self.talk(answer)


                                # Handling complaints
                                elif any(user_input in text for user_input in self.language.USER_COMPLAINS):
                                    answer = random.choice(self.language.BOT_HANDLES_COMPLAINTS)
                                    self.talk(answer)


                                # Searching on wikipedia
                                elif any(user_input in text for user_input in self.language.USER_ASKS_TO_SEARCH):
                                    for user_input in self.language.USER_ASKS_TO_SEARCH:
                                        if user_input in text:
                                            query = text.replace(user_input, "").strip()


                                    speech = self.language.BOT_SEARCHES_INFO.replace("query", query)
                                    self.talk(speech, mood="loading")
                                    try:
                                        search_result = wikipedia.summary(query, sentences=1)
                                        print(search_result)
                                        self.talk(self.language.SEARCH_RESULT + search_result)
                                    except wikipedia.exceptions.PageError:
                                        self.talk(self.language.NO_SEARCH_RESULTS)
                                    except wikipedia.exceptions.DisambiguationError:
                                        answer = self.language.DISAMBIGUATION_ERROR.replace("query", query)
                                        self.talk(answer)
                                    except requests.exceptions.JSONDecodeError:
                                        self.talk(self.language.ERROR_DURING_RESEARCH)
                                    except wikipedia.exceptions.WikipediaException:
                                        self.talk(self.language.ERROR_DURING_RESEARCH)



                                elif any(user_input in text for user_input in self.language.USER_SEARCHES_ON_YT):
                                    query = text
                                    for words in self.language.USER_SEARCHES_ON_YT:
                                        if words in query:
                                            query = query.replace(words, "").strip()

                                    self.talk(self.language.BOT_PLAYS_VIDEO.replace("query", query))
                                    print(f"search on youtube: {query}")
                                    pywhatkit.playonyt(query)



                                # Opens WhatsApp
                                elif self.language.OPEN_WHATSAPP in text:
                                    self.talk(self.language.BOT_OPENS_WHATSAPP)
                                    AppOpener.open("whatsapp")



                                # Opens Google
                                elif self.language.OPEN_GOOGLE in text:
                                    self.talk(self.language.BOT_OPENS_GOOGLE)
                                    AppOpener.open("google chrome")



                                # Tells a joke
                                elif any(user_input in text for user_input in self.language.ASK_JOKE):
                                    joke = pyjokes.get_joke(language=self.lang, category="all")
                                    print(f"joke: {joke}")
                                    self.talk(joke)


                                # Bot goes to sleep
                                elif self.language.SEND_BOT_TO_SLEEP in text:
                                    answer = random.choice(self.language.BOT_GOES_TO_SLEEP)
                                    self.talk(answer)

                                    self.set_img_sleep()
                                    self.is_active = False


                                elif text is not None:
                                    self.talk(self.language.NOT_UNDERSTOOD)
                                    continue

                                else:
                                    continue

                            except speech_recognition.UnknownValueError:
                                continue

            except speech_recognition.UnknownValueError:
                continue






bot = Bot()