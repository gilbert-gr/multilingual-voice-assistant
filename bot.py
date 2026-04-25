import inputs_outputs_ita
from tkinter import *
from PIL import Image, ImageTk
import pandas as pd
import speech_recognition
import threading
import pyttsx3
import random
import pyjokes
import requests
from dotenv import load_dotenv
import os


load_dotenv()

IMAGE_SLEEP = Image.open("images/sleep.png")
IMAGE_LISTEN = Image.open("images/listen.png")
IMAGE_TALK = Image.open("images/talk.png")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEOCODING_ENDPOINT = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"


class Bot:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300

        self.root = Tk()
        self.root.title("Flick")

        self.root.geometry("424x632")

        self.active = False

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

    def talk(self, speech):
        self.set_img_talk()
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)
        engine.say(speech)
        engine.runAndWait()
        self.set_img_listen()

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
                        data = pd.read_csv("user-data.csv")
                        if data["name"][0] == "x":
                            answer = random.choice(inputs_outputs_ita.BOT_SALUTA).replace("utente", "")
                            self.talk(answer)
                            if random.randint(1, 5) == 1:
                                self.talk("se vuoi impostare un nome, dimmi il mio nome è più il tuo nome")
                        else:
                            answer = random.choice(inputs_outputs_ita.BOT_SALUTA).replace("utente", data["name"][0])
                            self.talk(answer)

                        self.active = True

                        while self.active:
                            try:
                                self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                                audio = self.recognizer.listen(mic)
                                text = self.recognizer.recognize_google(audio, language="it-IT")
                                text = text.lower()
                                print(text)



                                # Set username
                                if "il mio nome è" in text:
                                    try:
                                        split = text.split()
                                        user_name_index = split.index("è") + 1
                                        user_name = split[user_name_index]
                                        self.talk(f"Il tuo nome è {user_name}, conferma dicendo sì o no")
                                        confirm = False

                                    except IndexError:
                                        self.talk("non ho capito")
                                        continue

                                    while not confirm:
                                            try:
                                                audio = self.recognizer.listen(mic)
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
                                                    self.talk("mi spiace, non ho capito")


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
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                confirm_text = self.recognizer.recognize_google(audio, language="it-IT")
                                                confirm_text = confirm_text.lower().split()
                                                print(confirm_text)

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
                                                    self.talk("mi spiace, non ho capito")


                                            except speech_recognition.UnknownValueError:
                                                self.talk("non ho capito, puoi ripetere?")


                                # Get weather
                                elif "meteo" in text or "che tempo fa" in text:
                                    if data["location"][0] == "x":
                                        self.talk("non c'è un luogo impostato al momento, dimmi la tua località")
                                        location = False

                                        while not location:
                                            try:
                                                audio = self.recognizer.listen(mic)
                                                user_location = self.recognizer.recognize_google(audio, language="it-IT")
                                                user_location = user_location.lower()
                                                print(f"location: {user_location}")

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
                                                    self.talk(f"{user_location} impostata come località, per cambiarla"
                                                              f"dimmi cambia località")
                                                    location = True

                                                except IndexError:
                                                    self.talk("località non trovata, prego ripeti")


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
                                              f"Domani invece sarà {tomorrow_description} e le temperature intorno"
                                              f"ai {tomorrow_temperature} gradi")



                                # Change user location
                                elif "cambia località" in text:
                                    self.talk("dimmi la tuà località")
                                    location = False

                                    while not location:
                                        try:
                                            audio = self.recognizer.listen(mic)
                                            user_location = self.recognizer.recognize_google(audio, language="it-IT")
                                            user_location = user_location.lower()
                                            print(f"location: {user_location}")

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
                                                self.talk(f"{user_location} impostata come località, per cambiarla"
                                                          f"dimmi cambia località")
                                                location = True

                                            except IndexError:
                                                self.talk("località non trovata, prego ripeti")



                                        except speech_recognition.UnknownValueError:
                                            self.talk("non ho capito, puoi ripetere?")




                                # Asking how is going
                                elif any(user_input in text for user_input in inputs_outputs_ita.USER_CHIEDE_COME_VA):
                                    answer = random.choice(inputs_outputs_ita.BOT_RISPONDE_COME_VA)
                                    self.talk(answer)


                                # Saying thank you
                                elif any(user_input in text for user_input in inputs_outputs_ita.USER_RINGRAZIA):
                                    answer = random.choice(inputs_outputs_ita.BOT_RISPONDE_A_GRAZIE)
                                    self.talk(answer)


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
                                    self.active = False

                                else:
                                    pass

                            except speech_recognition.UnknownValueError:
                                continue

            except speech_recognition.UnknownValueError:
                continue
