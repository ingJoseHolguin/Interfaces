import requests
import json

LM_STUDIO_API_URL = "http://localhost:1234/api/v0/chat/completions"

def identificar_modelos():
    """
    Función para identificar los modelos disponibles en LM Studio.

    Returns:
        list: Lista de modelos disponibles
    """
    # URL para la API de LM Studio
    url = "http://localhost:1234/api/v0/models"

    try:
        # Enviar la solicitud al servidor
        respuesta = requests.get(url)

        # Verificar si la solicitud fue exitosa
        if respuesta.status_code == 200:
            # Extraer y devolver solo los nombres de los 
            data = json.loads(respuesta.text)
            modelo1 = data["data"][0]["id"]
            return modelo1
        else:
            print(f"Error: Código de estado {respuesta.status_code}")
            return []

    except Exception as e:
        print(f"Error al conectar con LM Studio: {e}")
        return []

# 0.0-0.3: Muy determinista, bueno para tareas que requieren precisión
# 0.4-0.7: Equilibrio entre creatividad y coherencia
# 0.8-1.0: Más aleatorio, bueno para generación creativa
def consultar_modelo(mensajes,temperatura):
    """
    Función para consultar el modelo en LM Studio.
    
    Args:
        mensajes (list): Lista de mensajes para el chat
        
        
    Returns:
        str: La respuesta del modelo
    """
    model = identificar_modelos()
    print("Modelo: <"+ model + ">")
    
    # Datos para enviar en la solicitud
    datos = {
        "model": model,
        "messages": mensajes,  # Usar directamente la lista de mensajes
        "temperatura": temperatura
    }
    
    try:
        # Enviar la solicitud al servidor
        respuesta = requests.post(LM_STUDIO_API_URL, json=datos)
        
        # Verificar si la solicitud fue exitosa
        if respuesta.status_code == 200:
            # Extraer y devolver solo el texto de la respuesta
            return respuesta.json()["choices"][0]["message"]["content"]
        else:
            print(f"Error: Código de estado {respuesta.status_code}")
            print(respuesta.text)  # Mostrar el texto del error para diagnóstico
            return "error servidor.... codigo " + str(respuesta.status_code)
    
    except Exception as e:
        print(f"Error al conectar con LM Studio: {e}")
        return "Error de conexión: " + str(e)
    

# Ejemplo de uso
if __name__ == "__main__":
    # Mensaje para el modelo
    pregunta = "Escribe una función en Python para calcular la secuencia de Fibonacci recursivamente."
    
    print("Consultando al modelo...")
    respuesta = consultar_modelo(pregunta,0.7)
    
    if respuesta:
        print("\nRespuesta:")
        print("-" * 50)
        print(respuesta)
        print("-" * 50)
    else:
        print("\nNo se pudo obtener una respuesta. Asegúrate de que LM Studio esté ejecutándose.")