import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()

    engine.setProperty("rate", 150)  # Ajusta la velocidad
    voices = engine.getProperty("voices")

    for voice in voices:
        if "spanish" in voice.name.lower() or "español" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    text_to_speech("test de voz sintetica")

