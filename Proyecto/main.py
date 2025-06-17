import requests
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import pyttsx3
import subprocess
import webbrowser
import os
import time


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
        
        print("Asistente de voz iniciado. Di 'hola asistente' para comenzar.")
    
    def configurar_voz(self):
        """Configura la voz del asistente"""
        self.tts_engine.setProperty("rate", 180)
        voices = self.tts_engine.getProperty("voices")
        
        for voice in voices:
            if "spanish" in voice.name.lower() or "español" in voice.name.lower():
                self.tts_engine.setProperty("voice", voice.id)
                break
    
    def hablar(self, texto):
        """Convierte texto a voz"""
        print(f"Asistente: {texto}")
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
            # Respuestas básicas sin IA cuando LM Studio no está disponible
            return self.respuesta_basica(mensaje)
        
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
            return self.respuesta_basica(mensaje)
    
    def respuesta_basica(self, mensaje):
        """Respuestas básicas cuando no hay LLM disponible"""
        mensaje_lower = mensaje.lower()
        
        # Comandos de sistema
        if any(word in mensaje_lower for word in ["abre", "abrir", "ejecuta"]):
            if "navegador" in mensaje_lower or "browser" in mensaje_lower:
                return "[COMANDO]ABRIR_NAVEGADOR[/COMANDO] Perfecto, abriendo el navegador web."
            elif "word" in mensaje_lower:
                return "[COMANDO]ABRIR_WORD[/COMANDO] Abriendo Microsoft Word para ti."
            elif "excel" in mensaje_lower:
                return "[COMANDO]ABRIR_EXCEL[/COMANDO] Abriendo Microsoft Excel."
            elif "calculadora" in mensaje_lower:
                return "[COMANDO]ABRIR_CALCULADORA[/COMANDO] Abriendo la calculadora."
            elif "notepad" in mensaje_lower or "bloc" in mensaje_lower:
                return "[COMANDO]ABRIR_NOTEPAD[/COMANDO] Abriendo el bloc de notas."
        
        # Búsquedas
        elif "busca" in mensaje_lower or "buscar" in mensaje_lower:
            # Extraer qué buscar
            terminos_busqueda = mensaje_lower.replace("busca", "").replace("buscar", "").strip()
            if terminos_busqueda:
                return f"[COMANDO]BUSCAR:{terminos_busqueda}[/COMANDO] Buscando '{terminos_busqueda}' en Google."
            else:
                return "¿Qué quieres que busque?"
        
        # Control de volumen
        elif "volumen" in mensaje_lower:
            if "sube" in mensaje_lower or "subir" in mensaje_lower or "alto" in mensaje_lower:
                return "[COMANDO]VOLUMEN_SUBIR[/COMANDO] Subiendo el volumen del sistema."
            elif "baja" in mensaje_lower or "bajar" in mensaje_lower or "bajo" in mensaje_lower:
                return "[COMANDO]VOLUMEN_BAJAR[/COMANDO] Bajando el volumen del sistema."
            elif "silencio" in mensaje_lower or "mute" in mensaje_lower:
                return "[COMANDO]VOLUMEN_SILENCIAR[/COMANDO] Silenciando el audio del sistema."
        
        # Saludos y conversación básica
        elif any(word in mensaje_lower for word in ["hola", "buenos días", "buenas tardes", "buenas noches"]):
            return "¡Hola! Soy tu asistente de voz. Puedo ayudarte a controlar tu computadora o buscar información. ¿En qué puedo ayudarte?"
        
        elif any(word in mensaje_lower for word in ["cómo estás", "qué tal", "como estas"]):
            return "Estoy funcionando perfectamente y listo para ayudarte. ¿Qué necesitas que haga?"
        
        elif any(word in mensaje_lower for word in ["gracias", "muy bien", "perfecto"]):
            return "¡De nada! Estoy aquí para ayudarte cuando lo necesites."
        
        elif any(word in mensaje_lower for word in ["chiste", "broma", "diversión"]):
            chistes = [
                "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae a los bugs.",
                "¿Cómo llamas a un programador que no documenta su código? Un arqueólogo del futuro.",
                "¿Por qué Python es como un buen chiste? Porque es fácil de entender."
            ]
            import random
            return random.choice(chistes)
        
        elif "hora" in mensaje_lower or "tiempo" in mensaje_lower:
            import datetime
            ahora = datetime.datetime.now()
            return f"Son las {ahora.strftime('%H:%M')} del {ahora.strftime('%d de %B de %Y')}."
        
        elif "ayuda" in mensaje_lower or "qué puedes hacer" in mensaje_lower:
            return """Puedo ayudarte con:
            • Abrir aplicaciones: 'Abre Word', 'Abre el navegador'
            • Buscar en Google: 'Busca recetas de pasta'
            • Controlar volumen: 'Sube el volumen'
            • Conversación básica y chistes
            • Decirte la hora actual"""
        
        else:
            return "Entiendo que quieres decirme algo, pero sin el LM Studio solo puedo ayudarte con comandos básicos. Di 'ayuda' para ver qué puedo hacer."
    
    def ejecutar_comando(self, comando):
        """Ejecuta comandos del sistema"""
        try:
            if comando == "ABRIR_NAVEGADOR":
                webbrowser.open("https://www.google.com")
                return "Abriendo navegador web"
            
            elif comando == "ABRIR_WORD":
                excel_path = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
                subprocess.Popen([excel_path])
                return "Abriendo Microsoft Word"
            
            elif comando == "ABRIR_EXCEL":
                excel_path = r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"
                subprocess.Popen([excel_path])
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
        
        print("Escuchando... Di algo:")
        
        while self.escuchando:
            try:
                data = stream.read(4096, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    texto = json.loads(result)["text"]
                    if texto:
                        print(f"Usuario: {texto}")
                        return texto
                else:
                    partial_result = json.loads(self.recognizer.PartialResult())["partial"]
                    if partial_result:
                        print(f"Escuchando: {partial_result}", end="\r")
            except Exception as e:
                print(f"Error en reconocimiento de voz: {e}")
                time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        mic.terminate()
        return None
    
    def ejecutar(self):
        """Bucle principal del asistente"""
        self.hablar("Hola, soy tu asistente virtual comandado por voz. ¿En qué puedo ayudarte?")
        
        while True:
            try:
                texto_usuario = self.escuchar_voz()
                
                if not texto_usuario:
                    continue
                
                if "adiós asistente" in texto_usuario.lower() or "cerrar asistente" in texto_usuario.lower():
                    self.hablar("Hasta luego. Que tengas un buen día.")
                    break
                
                elif "silencio" in texto_usuario.lower() or "cállate" in texto_usuario.lower():
                    print("Asistente en modo silencioso. Di 'hola asistente' para reactivar.")
                    while True:
                        texto = self.escuchar_voz()
                        if texto and "hola asistente" in texto.lower():
                            self.hablar("Ya estoy aquí. ¿En qué puedo ayudarte?")
                            break
                    continue
                
                print("Procesando...")
                respuesta_llm = self.consultar_llm(texto_usuario)
                
                respuesta_final = self.procesar_respuesta(respuesta_llm)
                self.hablar(respuesta_final)
                
            except KeyboardInterrupt:
                print("\nCerrando asistente...")
                self.hablar("Hasta luego")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.hablar("Disculpa, tuve un problema. ¿Puedes repetir?")

def main():
    print("=" * 60)
    print(" ASISTENTE DE VOZ CON CONTROL DE PC")
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
    
    try:
        response = requests.get("http://localhost:1234/api/v0/models", timeout=5)
        if response.status_code != 200:
            print("⚠️  ADVERTENCIA: LM Studio no parece estar ejecutándose.")
            print("   El asistente funcionará solo con comandos básicos.")
            respuesta = input("¿Continuar de todos modos? (s/n): ")
            if respuesta.lower() != 's':
                return
    except:
        print(" ERROR: No se puede conectar con LM Studio.")
        print("   SOLUCIÓN:")
        print("   1. Abre LM Studio")
        print("   2. Carga un modelo")
        print("   3. Ve a 'Local Server' y haz clic en 'Start Server'")
        print("   4. Verifica que diga 'Server running on port 1234'")
        print()
        respuesta = input("¿Continuar sin IA? El asistente funcionará solo con comandos (s/n): ")
        if respuesta.lower() != 's':
            return
    
    asistente = AsistenteVoz()
    asistente.ejecutar()

if __name__ == "__main__":
    main()