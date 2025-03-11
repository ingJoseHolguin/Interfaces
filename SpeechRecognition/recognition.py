import whisper
import pyaudio
import wave
import tempfile
import os

model = None

# Model size parameters and requirements
# Size      | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed
# --------- | ----------| ------------------ | ------------------ | ------------- | ---------------
# tiny      | 39 M      | tiny.en           | tiny               | ~1 GB         | ~10x
# base      | 74 M      | base.en           | base               | ~1 GB         | ~7x
# small     | 244 M     | small.en          | small              | ~2 GB         | ~4x
# medium    | 769 M     | medium.en         | medium             | ~5 GB         | ~2x
# large     | 1550 M    | N/A               | large              | ~10 GB        | 1x
# turbo     | 809 M     | N/A               | turbo              | ~6 GB         | ~8x

def load_model(model_size):
    """Carga el modelo solo si no está cargado aún."""
    global model
    if model is None:
        print("Cargando el modelo...")
        model = whisper.load_model(model_size)
    else:
        print("El modelo ya está cargado.")
    return model


def record_audio(duration=5):
    
    chunk = 1024  # Tamaño del fragmento de audio
    format = pyaudio.paInt16  # Formato de audio
    channels = 1  # Mono
    rate = 16000  # Frecuencia de muestreo

    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wf = wave.open(f.name, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        return f.name

def transcribe_from_microphone():
    print("Escuchando: ")
    load_model("base")
    while True:
        audio_file = record_audio()
        result = model.transcribe(audio_file)
        print(f"Texto reconocido: {result['text']}")

def trascribe_from_file(audio_file):
    print("Escuchando: ")
    load_model("base")
    result = model.transcribe(audio_file)
    if os.path.exists(audio_file): #elimina el dichero generado
        os.remove(audio_file)
    else:
        print("⚠ El archivo no existe")   
    return result['text']

if __name__ == "__main__":
    transcribe_from_microphone() #ejemplo cada 5 segundos graba y describe lo que hizo.