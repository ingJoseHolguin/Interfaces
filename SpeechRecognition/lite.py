import json
import pyaudio
from vosk import Model, KaldiRecognizer

def recognition_lite():
    model = Model("vosk-model-small-es-0.42")  # Asegúrate de tener este modelo descargado
    recognizer = KaldiRecognizer(model, 16000)

    # Configurar el micrófono
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            texto = json.loads(result)["text"]
            if texto:
                print(f"Texto reconocido: {texto}")
                return texto
        else:
            partial_result = json.loads(recognizer.PartialResult())["partial"]
            if partial_result:
                print(f"Escuchando: {partial_result}", end="\r")