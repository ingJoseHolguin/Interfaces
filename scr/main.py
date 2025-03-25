import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SpeechRecognition import lite as recognition_lite
from TextToSpeech import lite  
from lmstudio import lmstudio
import pywhatkit 

# inicializa el lm studio
# lms server start

def analizar_oracion(oracion):
    mensaje = [
        {"role": "system", "content": "Eres un asistente lingüístico especializado. Tu tarea es analizar gramática y semántica de oraciones en español y responder ÚNICAMENTE en formato JSON válido."},
        {"role": "user", "content": f"""
        Analiza esta oración: "{oracion}"
        
        Responde ÚNICAMENTE en formato JSON con la siguiente estructura exacta crea el analisis de la oracion en los campos correspondientes del json, es extrictor respetar la rspuestas con el siguiente formato
        {{
            "análisis_gramatical": "Descripcion del analisis grmatical",            
            "análisis_semántico": "interpretación del significado y la semantica",
            "verbo": "en este campo deja el verbo de la oracion",
            "complemento": "en este campo se llena con el complemento de la oracion"
            "ejecutar": True
            }}       
        Si la oración contiene un verbo que indica una acción ejecutable (como reproducir, abrir, buscar, etc.), marca "ejecutar" como True.
        """}
    ]
    return mensaje

if __name__ == "__main__":
    print("Inicio")
    lite.text_to_speech("Hola, ¿en qué puedo ayudarte?")
    while True:
        # Obtener texto reconocido (esto ya debe ser un string)
        usuario = recognition_lite.recognition_lite()
        print(f"Texto reconocido: {usuario}")
        
        if usuario != "":
           # Enviar directamente la lista de mensajes
           respuestatexto = lmstudio.consultar_modelo(analizar_oracion(usuario),0.1)
           respuesta = json.loads(respuestatexto)
           print(respuesta)
           if respuesta["ejecutar"] == True:
               pywhatkit.playonyt(respuesta["complemento"])
           lite.text_to_speech(respuestatexto)
    



            




