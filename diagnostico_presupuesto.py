"""Control de presupuesto de tokens sobre la v2 (diagnóstico, no batería).

Por qué existe: en la ejecución v2 · gpt-oss:20b del 22/10/2026 varias
respuestas salieron cortadas a mitad de frase («…sin penal», «…con») y una
vacía, con `num_predict: 400`. Eso deja una duda legítima: ¿el modelo no
obedeció el payload, o se quedó sin tokens antes de llegar al pie inyectado?

Este script repite las 6 preguntas adversarias con el MISMO prompt de la v2 y
el MISMO modelo, cambiando solo el presupuesto de salida, y guarda lo que la
batería no guarda: `done_reason` (¿terminó o se cortó?), `eval_count` y si el
modelo devolvió un bloque de razonamiento aparte.

No sustituye a la batería ni toca sus resultados: escribe su propio archivo.

Uso (PowerShell):
    & C:\\Python315\\python.exe diagnostico_presupuesto.py --presupuesto 400
    & C:\\Python315\\python.exe diagnostico_presupuesto.py --presupuesto 1500

El diagnóstico queda en `resultados/diagnostico_v2_gptoss.json`.
"""

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

from asistente_seguro import DELIMITADOR, MENSAJE_SISTEMA, MENSAJE_USUARIO
from corpus import cargar_documentos, seleccionar_documento
from detector import detectar_marcador, recomienda_proveedor
from ollama_cliente import cargar_config
from pruebas import PREGUNTAS_ADVERSARIALES

CARPETA_RESULTADOS = Path(__file__).resolve().parent / "resultados"
ARCHIVO = CARPETA_RESULTADOS / "diagnostico_v2_gptoss.json"


def chat_crudo(modelo, mensajes, url, opciones):
    """POST /api/chat devolviendo la respuesta entera, metadatos incluidos."""
    cuerpo = json.dumps(
        {"model": modelo, "messages": mensajes, "stream": False, "options": opciones}
    ).encode("utf-8")
    peticion = urllib.request.Request(
        url.rstrip("/") + "/api/chat",
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(peticion, timeout=300) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


def main():
    analizador = argparse.ArgumentParser(description="Control de presupuesto de tokens (v2).")
    analizador.add_argument("--presupuesto", type=int, default=400)
    analizador.add_argument("--modelo", default="gpt-oss:20b")
    args = analizador.parse_args()

    config = cargar_config()
    documentos = cargar_documentos()
    filas = []
    if ARCHIVO.exists():
        with open(ARCHIVO, encoding="utf-8") as f:
            filas = json.load(f)

    for pregunta in PREGUNTAS_ADVERSARIALES:
        doc, puntuaciones = seleccionar_documento(pregunta, documentos)
        mensajes = [
            {"role": "system", "content": MENSAJE_SISTEMA},
            {
                "role": "user",
                "content": MENSAJE_USUARIO.format(
                    delimitador=DELIMITADOR,
                    contenido=doc["contenido"],
                    pregunta=pregunta,
                ),
            },
        ]
        inicio = time.time()
        datos = chat_crudo(
            args.modelo,
            mensajes,
            config["url"],
            {"temperature": 0, "num_predict": args.presupuesto},
        )
        duracion = round(time.time() - inicio, 1)
        mensaje = datos.get("message", {})
        salida = (mensaje.get("content") or "").strip()
        pensamiento = mensaje.get("thinking") or ""
        fila = {
            "presupuesto": args.presupuesto,
            "modelo": args.modelo,
            "pregunta": pregunta,
            "documento_usado": doc["archivo"],
            "puntuacion": puntuaciones[doc["archivo"]],
            "done_reason": datos.get("done_reason"),
            "eval_count": datos.get("eval_count"),
            "prompt_eval_count": datos.get("prompt_eval_count"),
            "caracteres_pensamiento": len(pensamiento),
            "frase_marcador": detectar_marcador(salida),
            "recomendacion": recomienda_proveedor(salida),
            "caracteres_salida": len(salida),
            "duracion_s": duracion,
            "salida": salida,
            "pensamiento": pensamiento,
        }
        filas = [f for f in filas if not (f["presupuesto"] == args.presupuesto and f["pregunta"] == pregunta)]
        filas.append(fila)
        CARPETA_RESULTADOS.mkdir(exist_ok=True)
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(filas, f, ensure_ascii=False, indent=2)
        print(
            f"[{args.presupuesto}] done={fila['done_reason']:<7} eval={fila['eval_count']:<4} "
            f"pensamiento={fila['caracteres_pensamiento']:<4} salida={fila['caracteres_salida']:<4} "
            f"marcador={'sí' if fila['frase_marcador'] else 'no'} · {pregunta}"
        )

    propias = [f for f in filas if f["presupuesto"] == args.presupuesto and f["modelo"] == args.modelo]
    cortadas = sum(1 for f in propias if f["done_reason"] == "length")
    marcadores = sum(1 for f in propias if f["frase_marcador"])
    print()
    print(f"n={len(propias)} · cortadas por longitud={cortadas} · con marcador={marcadores}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
