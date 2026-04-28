import inputs_outputs_ita
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


load_dotenv()

IMAGE_SLEEP = Image.open("images/sleep.png")
IMAGE_LISTEN = Image.open("images/listen.png")
IMAGE_TALK = Image.open("images/talk.png")
IMAGE_TIMER = Image.open("images/timer.png")
IMAGE_LOADING = Image.open("images/loading.png")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEOCODING_ENDPOINT = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"

wikipedia.set_lang("it")


class Bot:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300

        self.root = Tk()
        self.root.title("Flick")

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
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)
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
                self.talk("timer finito, premi enter per interrompermi", mood="timer")
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
                print("parla")
                with speech_recognition.Microphone() as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                    audio = self.recognizer.listen(mic)

                    text = self.recognizer.recognize_google(audio, language="it-IT")
                    text = text.lower()
                    print(text)

                    # Bot activates
                    if "ok" in text:
                        self.is_active = True

                        data = pd.read_csv("user-data.csv")
                        if data["name"][0] == "x":
                            answer = random.choice(inputs_outputs_ita.BOT_SALUTA).replace("utente", "")
                            self.talk(answer)
                            if random.randint(1, 5) == 1:
                                self.talk("se vuoi impostare un nome, dimmi il mio nome è più il tuo nome")
                        else:
                            answer = random.choice(inputs_outputs_ita.BOT_SALUTA).replace("utente", data["name"][0])
                            self.talk(answer)

                        while self.is_active:
                            try:
                                self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                                audio = self.recognizer.listen(mic)
                                text = self.recognizer.recognize_google(audio, language="it-IT")
                                text = text.lower()
                                print(text)



                                # Set username
                                if "mio nome è" in text:
                                    try:
                                        split = text.split()
                                        user_name_index = split.index("è") + 1
                                        user_name = split[user_name_index]
                                        if user_name == "x":
                                            self.talk("nome non valido")
                                            continue
                                        self.talk(f"Il tuo nome è {user_name}, conferma dicendo sì o no")
                                        confirm = False

                                    except IndexError:
                                        self.talk("non ho capito")
                                        continue

                                    while not confirm:
                                        self.wait_if_is_talking()
                                        try:
                                            audio = self.recognizer.listen(mic)
                                            if self.is_talking:
                                                continue
                                            confirm_text = self.recognizer.recognize_google(audio, language="it-IT")
                                            confirm_text = confirm_text.lower().split()
                                            print(confirm_text)

                                            if "sì" in confirm_text:
                                                data.loc[0, "name"] = user_name
                                                data.to_csv("user-data.csv", index=False)

                                                self.talk(
                                                    "Okay, memorizzato! se in seguito vuoi modificarlo dimmi il "
                                                    "mio nome è più il tuo nome, per eliminarlo dimmi elimina "
                                                    "il mio nome")
                                                confirm = True
                                                continue

                                            if "no" in confirm_text:
                                                self.talk("mi spiace, se vuoi impostare un nome, dimmi il mio nome "
                                                          "è più il tuo nome")
                                                confirm = True

                                            else:
                                                self.talk("mi spiace, non ho capito, dimmi sì o no")


                                        except speech_recognition.UnknownValueError:
                                            self.talk("non ho capito, puoi ripetere?")



                                # Delete username
                                elif "elimina il mio nome" in text:
                                    data = pd.read_csv("user-data.csv")
                                    if data["name"][0] == "x":
                                        self.talk("non c'è nessun nome impostato al momento")
                                    else:
                                        name_to_delete = data["name"][0]
                                        self.talk(f"il nome attuale è {name_to_delete}, vuoi eliminarlo? "
                                                  f"Conferma dicendo sì o no")

                                        confirm = False

                                        while not confirm:
                                            self.wait_if_is_talking()
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                if self.is_talking:
                                                    continue
                                                confirm_text = self.recognizer.recognize_google(audio, language="it-IT")
                                                confirm_text = confirm_text.lower().split()
                                                print(confirm_text)

                                                self.wait_if_is_talking()

                                                if "sì" in confirm_text:
                                                    data.loc[0, "name"] = "x"
                                                    data.to_csv("user-data.csv", index=False)

                                                    self.talk("nome eliminato con successo")
                                                    confirm = True
                                                    continue

                                                if "no" in confirm_text:
                                                    self.talk("d'accordo se cambi idea ripeti il comando")
                                                    confirm = True

                                                else:
                                                    self.talk("mi spiace, non ho capito, dimmi sì o no")


                                            except speech_recognition.UnknownValueError:
                                                self.talk("non ho capito, puoi ripetere?")


                                # Get weather
                                elif "meteo" in text or "che tempo fa" in text:
                                    if data["location"][0] == "x":
                                        self.talk("non c'è un luogo impostato al momento, dimmi la tua località")
                                        location = False

                                        while not location:
                                            self.wait_if_is_talking()
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                if self.is_talking:
                                                    continue
                                                user_location = self.recognizer.recognize_google(audio, language="it-IT")
                                                user_location = user_location.lower()
                                                print(f"location: {user_location}")

                                                self.wait_if_is_talking()

                                                if user_location == "x":
                                                    self.talk("località non valida, prego ripeti")
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
                                                    self.talk(f"{user_location} impostata come località, in futuro, per"
                                                          f"cambiarla dimmi cambia località")
                                                    location = True

                                                except IndexError:
                                                    self.talk("località non trovata, prego ripeti solo il nome della"
                                                              "località")


                                            except speech_recognition.UnknownValueError:
                                                self.talk("non ho capito, puoi ripetere?")


                                    else:
                                        user_location = data["location"][0]
                                        user_lat = data["lat"][0]
                                        user_lon = data["lon"][0]
                                        print(f"location:{user_location}\nlat: {user_lat}\nlon: {user_lon}")


                                    params = {
                                        "lat": user_lat,
                                        "lon": user_lon,
                                        "appid": WEATHER_API_KEY,
                                        "lang": "it",
                                        "units": "metric"
                                    }

                                    response = requests.get(WEATHER_FORECAST_ENDPOINT, params=params)
                                    response.raise_for_status()

                                    today_description = response.json()["list"][1]["weather"][0]["description"]
                                    today_temperature = response.json()["list"][1]["main"]["temp"]
                                    tomorrow_description = response.json()["list"][8]["weather"][0]["description"]
                                    tomorrow_temperature = response.json()["list"][8]["main"]["temp"]

                                    self.talk(f"Il tempo di oggi a {user_location} sarà {today_description} e le"
                                              f"temperature si aggireranno intorno ai {today_temperature} gradi celsius"
                                              f"Invece domani sarà {tomorrow_description} e le temperature intorno"
                                              f"ai {tomorrow_temperature} gradi")



                                # Change user location
                                elif "cambia località" in text:
                                    self.talk("dimmi la tuà località")
                                    location = False

                                    while not location:
                                        self.wait_if_is_talking()
                                        try:
                                            audio = self.recognizer.listen(mic)
                                            if self.is_talking:
                                                continue
                                            user_location = self.recognizer.recognize_google(audio, language="it-IT")
                                            user_location = user_location.lower()
                                            print(f"location: {user_location}")

                                            self.wait_if_is_talking()

                                            if user_location == "x":
                                                self.talk("località non valida, prego ripeti")
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
                                                self.talk(f"{user_location} impostata come località, in futuro, per "
                                                          f"cambiarla dimmi cambia località")
                                                location = True

                                            except IndexError:
                                                self.talk("località non trovata, prego ripeti solo il nome della"
                                                              "località")



                                        except speech_recognition.UnknownValueError:
                                            self.talk("non ho capito, puoi ripetere?")



                                # Set timer
                                elif "timer" in text:
                                    seconds_timer = 0
                                    minutes_timer = 0

                                    if self.timer != 0:
                                        self.talk("c'è già un timer in corso")
                                        continue
                                    if "secondi" in text:
                                        seconds_index = text.split().index("secondi")
                                        seconds_timer = text.split()[seconds_index - 1]
                                        if seconds_timer == "un":
                                            seconds_timer = 1
                                        if "minuti" in text:
                                            minutes_index = text.split().index("minuti")
                                            minutes_timer = text.split()[minutes_index - 1]
                                        elif "minuto" in text:
                                            minutes_timer = 1


                                    elif "minuti" in text:
                                            minutes_index = text.split().index("minuti")
                                            minutes_timer = text.split()[minutes_index - 1]
                                            if "secondo" in text:
                                                seconds_timer = 1

                                    elif "minuto" in text:
                                        minutes_timer = 1
                                        if "secondi" in text:
                                            seconds_index = text.split().index("secondi")
                                            seconds_timer = text.split()[seconds_index - 1]
                                        elif "secondo" in text:
                                            seconds_timer = 1

                                    elif "secondo" in text:
                                        seconds_timer = 1

                                    else:
                                        self.talk("Non ho capito di quanto tempo impostare il timer")

                                    self.timer = int(minutes_timer) * 60 + int(seconds_timer)

                                    if self.timer == 0:
                                        self.talk("non posso impostare un timer di zero secondi dai")
                                        continue

                                    if minutes_timer == 1:
                                        if seconds_timer == 1:
                                            self.talk(
                                                f"okay, imposto un timer di un minuto e un secondo")
                                            print(f"{minutes_timer} minuto e {seconds_timer} secondo")
                                        else:
                                            self.talk(
                                                f"okay, imposto un timer di un minuto e {seconds_timer} secondi")
                                            print(f"{minutes_timer} minuto e {seconds_timer} secondi")
                                    elif seconds_timer == 1:
                                        self.talk(
                                            f"okay, imposto un timer di {minutes_timer} minuti e un secondo")
                                        print(f"{minutes_timer} minuti e {seconds_timer} secondo")
                                    else:
                                        self.talk(
                                            f"okay, imposto un timer di {minutes_timer} minuti e {seconds_timer}"
                                            f"secondi")
                                        print(f"{minutes_timer} minuti e {seconds_timer} secondi")


                                    print(f"{self.timer} secondi totali")
                                    self.start_timer = time.time()
                                    threading.Thread(target=self.check_timer, daemon=True).start()





                                # Asking how is going
                                elif any(user_input in text for user_input in inputs_outputs_ita.USER_CHIEDE_COME_VA):
                                    answer = random.choice(inputs_outputs_ita.BOT_RISPONDE_COME_VA)
                                    self.talk(answer)


                                # Saying thank you
                                elif any(user_input in text for user_input in inputs_outputs_ita.USER_RINGRAZIA):
                                    answer = random.choice(inputs_outputs_ita.BOT_RISPONDE_A_GRAZIE)
                                    self.talk(answer)


                                # Searching on wikipedia
                                elif any(user_input in text for user_input in inputs_outputs_ita.USER_CHIEDE_DI_CERCARE):
                                    for user_input in inputs_outputs_ita.USER_CHIEDE_DI_CERCARE:
                                        if user_input in text:
                                            query = text.replace(user_input, "")

                                    self.talk(f"cerco informazionni su {query}")
                                    self.set_img_loading()
                                    try:
                                        search_result = wikipedia.summary(query, sentences=1)
                                        print(search_result)
                                        self.talk(f"ecco cos'ho trovato:{search_result}")
                                    except wikipedia.exceptions.PageError:
                                        self.talk("nessun risultato trovato")
                                    except wikipedia.exceptions.DisambiguationError:
                                        self.talk(f"ci sono diversi risultati per {query}, ho bisogno che tu sia"
                                                  f"più specifico")


                                # Plays something on youtube
                                elif "metti" in text and "un video" in text or "su youtube" in text or "una canzone di" in text:
                                    query = text
                                    for words in inputs_outputs_ita.USER_CERCA_SU_YT:
                                        if words in query:
                                            query = query.replace(words, "")

                                    self.talk(f"va bene metto un video di {query}")
                                    print(f"cerco su youtube: {query}")
                                    pywhatkit.playonyt(query)



                                # Opens WhatsApp
                                elif "apri whatsapp" in text:
                                    self.talk("va bene, ti apro whatsapp")
                                    AppOpener.open("whatsapp")


                                # Opens Google
                                elif "apri google" in text:
                                    self.talk("ti apro subito google")
                                    AppOpener.open("google chrome")



                                # Tells a joke
                                elif "barzelletta" in text or "battuta" in text:
                                    joke = pyjokes.get_joke(language="it", category="all")
                                    print(f"joke: {joke}")
                                    self.talk(joke)


                                # Bot goes to sleep
                                elif "dormi" in text:
                                    answer = random.choice(inputs_outputs_ita.BOT_SI_CONGEDA)
                                    self.talk(answer)

                                    self.set_img_sleep()
                                    self.is_active = False

                                else:
                                    continue

                            except speech_recognition.UnknownValueError:
                                continue

            except speech_recognition.UnknownValueError:
                continue
