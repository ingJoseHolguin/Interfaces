import pyaudio
import numpy as np
import webrtcvad
import wave
import tempfile
import time

# Configuración de audio
CHUNK = 1024  
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 16000  
VAD_MODE = 3  

# Inicializar WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(VAD_MODE)

def is_speech(frame, rate=RATE):
    """Detecta si hay voz en un fragmento de audio."""
    frame_duration_ms = 30  
    frame_size = int(rate * (frame_duration_ms / 1000) * 2)  

    if len(frame) < frame_size:
        return False  

    return vad.is_speech(frame[:frame_size], rate)

def save_audio(frames):
    """Guarda el audio detectado en un archivo WAV y devuelve su ruta."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wf = wave.open(f.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        #print(f"🎙️ Audio guardado: {f.name}")
        return f.name  # Retorna la ruta del archivo guardado

def file_voice():
    """Graba audio cuando detecta voz y lo guarda tras 1 segundo de silencio."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    silent_frames = 0
    detecting = False  

    print("🎤 Esperando voz...")

    while True:
        audio_data = stream.read(CHUNK, exception_on_overflow=False)

        if is_speech(audio_data):
            if not detecting:
                print("🔴 Grabando...")
                detecting = True
            frames.append(audio_data)
            silent_frames = 0  
        elif detecting:
            silent_frames += 1
            if silent_frames > (RATE // CHUNK):  # 1 segundo de silencio
                print("🛑 Silencio detectado, guardando...")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()

    return save_audio(frames) if frames else None

# Ejemplo de uso:
if __name__ == "__main__":
    file_path = file_voice()
    if file_path:
        print(f"📁 Archivo guardado en: {file_path}")
