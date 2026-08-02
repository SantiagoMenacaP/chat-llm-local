import time
import requests
from typing import Dict, Any


class OllamaClient:
    """
    Cliente HTTP encargado exclusivamente de la comunicación con la API de Ollama.
    Mantiene alta cohesión al aislar las llamadas HTTP y la medición del tiempo de respuesta.
    """

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 120):
        """
        Inicializa el cliente de Ollama.

        :param base_url: URL base del servicio Ollama local.
        :param timeout: Tiempo máximo de espera en segundos para la API.
        """
        self.base_url = base_url.rstrip("/")
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.timeout = timeout

    def generate(self, model: str, prompt: str) -> Dict[str, Any]:
        """
        Envía un prompt a la API de Ollama (/api/generate) y mide el tiempo de respuesta.

        :param model: Nombre del modelo seleccionado (ej. 'gemma2:2b', 'llama3.2:3b').
        :param prompt: Texto ingresado por el usuario.
        :return: Diccionario con estado, respuesta, tiempo transcurrido (en segundos) y posibles errores.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        start_time = time.perf_counter()

        try:
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=self.timeout
            )
            elapsed_time = time.perf_counter() - start_time

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data.get("response", "").strip(),
                    "elapsed_time": round(elapsed_time, 2),
                    "error": None
                }
            else:
                error_msg = f"Error HTTP {response.status_code}: {response.text}"
                return {
                    "success": False,
                    "response": "",
                    "elapsed_time": round(elapsed_time, 2),
                    "error": error_msg
                }

        except requests.exceptions.ConnectionError:
            elapsed_time = time.perf_counter() - start_time
            return {
                "success": False,
                "response": "",
                "elapsed_time": round(elapsed_time, 2),
                "error": "No se pudo conectar con Ollama. Asegúrate de que el servidor esté activo en http://localhost:11434."
            }
        except requests.exceptions.Timeout:
            elapsed_time = time.perf_counter() - start_time
            return {
                "success": False,
                "response": "",
                "elapsed_time": round(elapsed_time, 2),
                "error": f"La solicitud superó el tiempo límite de espera ({self.timeout}s)."
            }
        except Exception as e:
            elapsed_time = time.perf_counter() - start_time
            return {
                "success": False,
                "response": "",
                "elapsed_time": round(elapsed_time, 2),
                "error": f"Error inesperado: {str(e)}"
            }
