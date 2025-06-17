import requests
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import pyttsx3
import subprocess
import webbrowser
import os
import time
import threading

class AsistenteVoz:
    def __init__(self):
        # Configuración del LLM
        self.LM_STUDIO_API_URL = "http://localhost:1234/api/v0/chat/completions"
        
        # Configuración del reconocimiento de voz
        self.model = Model("vosk-model-small-es-0.42")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        
        # Configuración del texto a voz
        self.tts_engine = pyttsx3.init()
        self.configurar_voz()
        
        # Historial de conversación
        self.historial_conversacion = []
        
        # Estado del asistente
        self.escuchando = True
        
        print("🤖 Asistente de voz iniciado. Di 'hola asistente' para comenzar.")
    
    def configurar_voz(self):
        """Configura la voz del asistente"""
        self.tts_engine.setProperty("rate", 150)
        voices = self.tts_engine.getProperty("voices")
        
        for voice in voices:
            if "spanish" in voice.name.lower() or "español" in voice.name.lower():
                self.tts_engine.setProperty("voice", voice.id)
                break
    
    def hablar(self, texto):
        """Convierte texto a voz"""
        print(f"🤖 Asistente: {texto}")
        self.tts_engine.say(texto)
        self.tts_engine.runAndWait()
    
    def identificar_modelos(self):
        """Identifica modelos disponibles en LM Studio"""
        url = "http://localhost:1234/api/v0/models"
        try:
            respuesta = requests.get(url)
            if respuesta.status_code == 200:
                data = json.loads(respuesta.text)
                return data["data"][0]["id"]
            else:
                return None
        except Exception as e:
            print(f"Error al conectar con LM Studio: {e}")
            return None
    
    def consultar_llm(self, mensaje, temperatura=0.7):
        """Consulta al modelo LLM"""
        model = self.identificar_modelos()
        if not model:
            return "Error: No se puede conectar con LM Studio"
        
        # Agregar contexto sobre comandos disponibles
        contexto_sistema = """Eres un asistente de voz útil. Puedes ayudar con información general y también controlar la computadora. 
        
        Si el usuario te pide hacer algo en la computadora, responde con el comando exacto entre [COMANDO] y [/COMANDO].
        
        Comandos disponibles:
        - [COMANDO]ABRIR_NAVEGADOR[/COMANDO] - Abre el navegador web
        - [COMANDO]ABRIR_WORD[/COMANDO] - Abre Microsoft Word
        - [COMANDO]ABRIR_EXCEL[/COMANDO] - Abre Microsoft Excel
        - [COMANDO]ABRIR_CALCULADORA[/COMANDO] - Abre la calculadora
        - [COMANDO]ABRIR_NOTEPAD[/COMANDO] - Abre el bloc de notas
        - [COMANDO]BUSCAR:{consulta}[/COMANDO] - Busca en Google
        - [COMANDO]VOLUMEN_SUBIR[/COMANDO] - Sube el volumen
        - [COMANDO]VOLUMEN_BAJAR[/COMANDO] - Baja el volumen
        - [COMANDO]VOLUMEN_SILENCIAR[/COMANDO] - Silencia el audio
        
        Responde de manera natural y amigable."""
        
        mensajes = [
            {"role": "system", "content": contexto_sistema},
            *self.historial_conversacion,
            {"role": "user", "content": mensaje}
        ]
        
        datos = {
            "model": model,
            "messages": mensajes,
            "temperature": temperatura
        }
        
        try:
            respuesta = requests.post(self.LM_STUDIO_API_URL, json=datos)
            if respuesta.status_code == 200:
                contenido = respuesta.json()["choices"][0]["message"]["content"]
                
                # Agregar al historial
                self.historial_conversacion.append({"role": "user", "content": mensaje})
                self.historial_conversacion.append({"role": "assistant", "content": contenido})
                
                # Mantener solo los últimos 10 intercambios
                if len(self.historial_conversacion) > 20:
                    self.historial_conversacion = self.historial_conversacion[-20:]
                
                return contenido
            else:
                return f"Error del servidor: {respuesta.status_code}"
        except Exception as e:
            return f"Error de conexión: {str(e)}"
    
    def ejecutar_comando(self, comando):
        """Ejecuta comandos del sistema"""
        try:
            if comando == "ABRIR_NAVEGADOR":
                webbrowser.open("https://www.google.com")
                return "Abriendo navegador web"
            
            elif comando == "ABRIR_WORD":
                subprocess.Popen(["winword"])
                return "Abriendo Microsoft Word"
            
            elif comando == "ABRIR_EXCEL":
                subprocess.Popen(["excel"])
                return "Abriendo Microsoft Excel"
            
            elif comando == "ABRIR_CALCULADORA":
                subprocess.Popen(["calc"])
                return "Abriendo calculadora"
            
            elif comando == "ABRIR_NOTEPAD":
                subprocess.Popen(["notepad"])
                return "Abriendo bloc de notas"
            
            elif comando.startswith("BUSCAR:"):
                consulta = comando.split("BUSCAR:")[1]
                webbrowser.open(f"https://www.google.com/search?q={consulta}")
                return f"Buscando '{consulta}' en Google"
            
            elif comando == "VOLUMEN_SUBIR":
                os.system("nircmd changesysvolume 2000")
                return "Subiendo volumen"
            
            elif comando == "VOLUMEN_BAJAR":
                os.system("nircmd changesysvolume -2000")
                return "Bajando volumen"
            
            elif comando == "VOLUMEN_SILENCIAR":
                os.system("nircmd mutesysvolume 1")
                return "Silenciando audio"
            
            else:
                return "Comando no reconocido"
                
        except Exception as e:
            return f"Error ejecutando comando: {str(e)}"
    
    def procesar_respuesta(self, respuesta_llm):
        """Procesa la respuesta del LLM y ejecuta comandos si los hay"""
        # Buscar comandos en la respuesta
        if "[COMANDO]" in respuesta_llm and "[/COMANDO]" in respuesta_llm:
            # Extraer comando
            inicio = respuesta_llm.find("[COMANDO]") + 9
            fin = respuesta_llm.find("[/COMANDO]")
            comando = respuesta_llm[inicio:fin]
            
            # Ejecutar comando
            resultado_comando = self.ejecutar_comando(comando)
            
            # Limpiar la respuesta del LLM (quitar etiquetas de comando)
            respuesta_limpia = respuesta_llm.replace(f"[COMANDO]{comando}[/COMANDO]", "")
            
            # Combinar respuesta con resultado del comando
            respuesta_final = f"{respuesta_limpia.strip()}. {resultado_comando}"
            
            return respuesta_final
        else:
            return respuesta_llm
    
    def escuchar_voz(self):
        """Escucha y reconoce voz"""
        mic = pyaudio.PyAudio()
        stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, 
                         input=True, frames_per_buffer=8192)
        stream.start_stream()
        
        print("🎤 Escuchando... Di algo:")
        
        while self.escuchando:
            try:
                data = stream.read(4096, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    texto = json.loads(result)["text"]
                    if texto:
                        print(f"👤 Usuario: {texto}")
                        return texto
                else:
                    partial_result = json.loads(self.recognizer.PartialResult())["partial"]
                    if partial_result:
                        print(f"🎤 Escuchando: {partial_result}", end="\r")
            except Exception as e:
                print(f"Error en reconocimiento de voz: {e}")
                time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        mic.terminate()
        return None
    
    def ejecutar(self):
        """Bucle principal del asistente"""
        self.hablar("Hola, soy tu asistente de voz. ¿En qué puedo ayudarte?")
        
        while True:
            try:
                # Escuchar entrada del usuario
                texto_usuario = self.escuchar_voz()
                
                if not texto_usuario:
                    continue
                
                # Comandos especiales para controlar el asistente
                if "adiós asistente" in texto_usuario.lower() or "cerrar asistente" in texto_usuario.lower():
                    self.hablar("Hasta luego. Que tengas un buen día.")
                    break
                
                elif "silencio" in texto_usuario.lower() or "cállate" in texto_usuario.lower():
                    print("🤖 Asistente en modo silencioso. Di 'hola asistente' para reactivar.")
                    while True:
                        texto = self.escuchar_voz()
                        if texto and "hola asistente" in texto.lower():
                            self.hablar("Ya estoy aquí. ¿En qué puedo ayudarte?")
                            break
                    continue
                
                # Procesar con LLM
                print("🧠 Procesando...")
                respuesta_llm = self.consultar_llm(texto_usuario)
                
                # Procesar comandos y responder
                respuesta_final = self.procesar_respuesta(respuesta_llm)
                self.hablar(respuesta_final)
                
            except KeyboardInterrupt:
                print("\n👋 Cerrando asistente...")
                self.hablar("Hasta luego")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.hablar("Disculpa, tuve un problema. ¿Puedes repetir?")

# Función principal
def main():
    print("=" * 60)
    print("🤖 ASISTENTE DE VOZ CON CONTROL DE PC")
    print("=" * 60)
    print("Características:")
    print("• Reconocimiento de voz en español")
    print("• Conversación con IA (LM Studio)")
    print("• Control de aplicaciones de Windows")
    print("• Búsquedas en Google por voz")
    print("• Control de volumen del sistema")
    print("=" * 60)
    print("\nComandos especiales:")
    print("• 'adiós asistente' - Cerrar el programa")
    print("• 'silencio' - Pausar el asistente")
    print("• 'hola asistente' - Reactivar asistente")
    print("\nEjemplos de uso:")
    print("• 'Abre el navegador'")
    print("• 'Busca recetas de pasta'")
    print("• 'Abre Word'")
    print("• 'Sube el volumen'")
    print("• 'Cuéntame un chiste'")
    print("=" * 60)
    
    # Verificar que LM Studio esté corriendo
    try:
        response = requests.get("http://localhost:1234/api/v0/models", timeout=5)
        if response.status_code != 200:
            print("⚠️  ADVERTENCIA: LM Studio no parece estar ejecutándose.")
            print("   Asegúrate de tener LM Studio abierto en el puerto 1234.")
            return
    except:
        print("❌ ERROR: No se puede conectar con LM Studio.")
        print("   Por favor, inicia LM Studio antes de ejecutar este programa.")
        return
    
    # Iniciar asistente
    asistente = AsistenteVoz()
    asistente.ejecutar()

if __name__ == "__main__":
    main()