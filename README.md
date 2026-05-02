# 🤖 Multilingual Voice Assistant

A high-performance desktop voice assistant built with Python, featuring a state-machine driven GUI and a modular asynchronous architecture.

The application provides a seamless interaction layer between the user and various cloud APIs such as Google Speech-to-Text, OpenWeatherMap, and Wikipedia.

---
## 📺 Demo

### 🎬 Check out the assistant in action:
[![Multilingual Voice Assistant Demo Research](https://img.youtube.com/vi/LyT-MjmvaLM/maxresdefault.jpg)](https://www.youtube.com/watch?v=LyT-MjmvaLM)
[![Multilingual Voice Assistant Demo](https://img.youtube.com/vi/d8zwXl5I4MY/hqdefault.jpg)](https://www.youtube.com/watch?v=d8zwXl5I4MY)


---
## 🚀 Key Features
### 🎙️ Core Interaction
+ Multilingual Processing
+ Dynamic support for English and Italian, switchable at runtime via GUI.
+ Acoustic Adaptation
+ Automatic ambient noise calibration for improved speech recognition accuracy.
+ State-Aware UI
+ Real-time visual feedback synchronized with the assistant state:
+ States: Sleep, Listen, Talk, Loading, Timer

---
### 🛠️ Functionalities (Voice Commands)
+ 👤 Identity Management
+ Set, confirm, and delete user profiles
+ Data stored locally with persistent storage
+ 🌦️ Meteorological Data
+ Current weather conditions
+ 24-hour forecast via OpenWeatherMap API
+ 📚 Knowledge Retrieval
+ Wikipedia search with automatic disambiguation handling
+ 🎯 Productivity & Entertainment
+ Voice-controlled countdown timers (visual + audio alerts)
+ Application launcher (e.g., WhatsApp, Google Chrome)
+ YouTube music/video playback
+ Random joke generator (PyJokes)

---
### 🧠 Architecture & Technical Decisions

+ Concurrency Management 

    Implemented using Python’s threading module to decouple:

    + Speech recognition (blocking I/O)
    + Text-to-speech
    + Tkinter GUI loop

    ➜ Result: 0% UI freezing

+ Modular i18n Strategy

    Language support handled through decoupled dictionaries:

  + inputs_outputs_en.py
  + inputs_outputs_it.py

  ➜ Enables runtime language injection

+ Persistent Storage

    Managed using CSV files 

    ➜ Lightweight and restart-safe data persistence

+ Input Protection System

    UI locking mechanisms (lock_ui, unlock_ui)

  ➜ Prevents race conditions from concurrent inputs

---
### 🛠️ Tech Stack

#### Backend

+ Python 3.x

#### GUI

+ Tkinter
+ Pillow (PIL)

#### Voice / NLP

+ SpeechRecognition (Google API)
+ Pyttsx3

#### Data Handling

+ Csv

#### APIs

+ OpenWeatherMap
+ Wikipedia
+ PyWhatKit

---
### ⚙️ Installation

1. Clone the repository
```bash
git clone https://github.com/gilbert-gr/multilingual-voice-assistant
cd multilingual-voice-assistant
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Environment Variables

Create a .env file in the root directory and add:
```env
WEATHER_API_KEY=your_api_key_here
```
4. Run the application
```bash
python bot_3.py
```

---
## 👨‍💻 Author

* 🔗 GitHub: https://github.com/gilbert-gr