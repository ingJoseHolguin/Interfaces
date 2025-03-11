from TTS.api import TTS
import torchaudio
import os
import subprocess

def humanizedText(texto,idioma):

    # Inicializar el modelo XTTS-v2 (usa GPU si está disponible)
    use_gpu = True if os.environ.get("CUDA_VISIBLE_DEVICES") else False
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)

    # Ruta al archivo de audio de referencia (voz a clonar)
    file_path = "C:/Users/jphol/Desktop/Maestria/DSI/code-Desarrollo/Interfaces/TextToSpeech/voz_referencia.wav"

    # Verificar que el archivo existe antes de cargarlo
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        exit()

    # Cargar el archivo de referencia
    try:
        audio, sr = torchaudio.load(file_path)
        print(f"Archivo cargado correctamente con sample rate: {sr}")
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        exit()
    
    # Generar el archivo de voz clonada
    archivo_salida = "TextToSpeech/voz_clonada_output.wav"
    try:
        tts.tts_to_file(
            text=texto,
            file_path=archivo_salida,
            speaker_wav=file_path,
            language=idioma
        )
        print(f"Archivo de voz generado: {archivo_salida}")
    except Exception as e:
        print(f"Error al generar la voz: {e}")
    
    subprocess.run(["ffplay", "-nodisp", "-autoexit", "TextToSpeech/voz_clonada_output.wav"])
    
    if os.path.exists(archivo_salida): #elimina el dichero generado
        os.remove(archivo_salida)
    else:
        print("⚠ El archivo no existe")   

    
if __name__ == "__main__":
    humanizedText("hola, este es un mensaje de prueba","es")
    subprocess.run(["ffplay", "-nodisp", "-autoexit", "HumanizedTextToSpeech/voz_clonada_output.wav"])

    