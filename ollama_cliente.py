"""Cliente mínimo para la API HTTP de Ollama.

Con urllib.request basta y sobra: no quería meter dependencias para hacer dos
POSTs. El proyecto entero usa solo biblioteca estándar, y eso es parte de la
gracia —no hay nada entre el código y lo que hay que auditar—.

Los dos endpoints que uso:

    POST /api/generate  →  un prompt suelto (lo usa la v1)
    POST /api/chat      →  mensajes con rol system/user (lo usa la v2)

Referencia de la API: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

import json
import urllib.error
import urllib.request
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
ARCHIVO_CONFIG = CARPETA / "config.json"

# Por si alguien borra el config.json o lo deja a medias: valores sensatos.
CONFIG_PREDETERMINADA = {
    "url": "http://localhost:11434",
    "modelo": "dolphin3:latest",
    "opciones": {"temperature": 0, "num_predict": 400},
}


def cargar_config():
    """Lee config.json (url, modelo y opciones)."""
    if not ARCHIVO_CONFIG.exists():
        return dict(CONFIG_PREDETERMINADA)
    with open(ARCHIVO_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    for clave, valor in CONFIG_PREDETERMINADA.items():
        config.setdefault(clave, valor)
    return config


def _llamar(ruta, cuerpo, timeout=300):
    peticion = urllib.request.Request(
        ruta,
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.URLError as error:
        # El fallo más común de todos: Ollama sin arrancar.
        raise SystemExit(
            "No se pudo conectar con Ollama en " + ruta + "\n"
            "Comprueba que el servidor está en marcha. En PowerShell:\n"
            "    Start-Process ollama -ArgumentList serve\n"
            "Detalle: " + repr(error)
        )


def generar(modelo, prompt, url="http://localhost:11434", opciones=None, timeout=300):
    """POST /api/generate con un prompt único. Devuelve el texto generado."""
    cuerpo = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "options": opciones if opciones is not None else {"temperature": 0, "num_predict": 400},
    }
    datos = _llamar(url.rstrip("/") + "/api/generate", cuerpo, timeout)
    return datos.get("response", "").strip()


def chat(modelo, mensajes, url="http://localhost:11434", opciones=None, timeout=300):
    """POST /api/chat con mensajes con rol. Devuelve el texto del asistente."""
    cuerpo = {
        "model": modelo,
        "messages": mensajes,
        "stream": False,
        "options": opciones if opciones is not None else {"temperature": 0, "num_predict": 400},
    }
    datos = _llamar(url.rstrip("/") + "/api/chat", cuerpo, timeout)
    return datos.get("message", {}).get("content", "").strip()
