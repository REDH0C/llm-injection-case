"""Los documentos del caso y la selección del documento relevante.

La selección es a propósito simple: solapamiento de palabras clave entre la
pregunta y el texto de cada documento. Podía montar algo con embeddings, pero
entonces el selector sería una caja negra más. Así se lee en quince líneas y
cualquiera puede auditar por qué se eligió cada documento.

Y esa trazabilidad importa: el asistente enseña siempre qué documento usó y
con qué puntuación, porque el caso va precisamente de datos recuperados.
"""

import re
import unicodedata
from pathlib import Path

CARPETA_DOCUMENTOS = Path(__file__).resolve().parent / "documentos"

ORDEN_DOCUMENTOS = [
    "politica_gastos.txt",
    "procedimiento_reembolsos.txt",
    "guia_viaplus_travel.txt",
]

# Palabras tan comunes que no sirven para distinguir un documento de otro.
PALABRAS_VACIAS = {
    "para", "por", "con", "que", "cual", "cuales", "como", "cuanto", "cuantos",
    "donde", "cuando", "debo", "debe", "puedo", "puede", "hay", "esta", "este",
    "esto", "sobre", "entre", "hasta", "desde", "una", "uno", "unos", "unas",
    "del", "las", "los", "les", "mis", "sus", "mas", "mismo", "tengo", "ser",
    "son", "sin", "todo", "todos", "toda", "todas", "algo", "alguna", "alguno",
    "trabajo", "empresa", "empleado", "asistente",
}


def normalizar(texto):
    """Minúsculas y sin tildes: para que 'política' encuentre 'politica'."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def _tokens(pregunta):
    """Las palabras de la pregunta que de verdad buscan documento (>= 4 letras, sin vacías)."""
    palabras = re.findall(r"[a-záéíóúüñ]+", normalizar(pregunta))
    return {p for p in palabras if len(p) >= 4 and p not in PALABRAS_VACIAS}


def cargar_documentos():
    """Lee los .txt de documentos/ y los devuelve como {archivo, titulo, contenido}."""
    rutas = []
    for nombre in ORDEN_DOCUMENTOS:
        ruta = CARPETA_DOCUMENTOS / nombre
        if ruta.exists():
            rutas.append(ruta)
    # Si algún día añado un cuarto documento, que cuente sin tocar el código.
    for ruta in sorted(CARPETA_DOCUMENTOS.glob("*.txt")):
        if ruta not in rutas:
            rutas.append(ruta)

    documentos = []
    for ruta in rutas:
        contenido = ruta.read_text(encoding="utf-8").strip()
        # El título es la primera línea con texto del propio documento.
        titulo = next(
            (linea.strip() for linea in contenido.splitlines() if linea.strip()),
            ruta.stem,
        )
        documentos.append({"archivo": ruta.name, "titulo": titulo, "contenido": contenido})
    return documentos


def seleccionar_documento(pregunta, documentos):
    """Gana el documento con más palabras clave de la pregunta dentro.

    Devuelve (documento, puntuaciones) para poder enseñar por qué ganó.
    """
    tokens = _tokens(pregunta)
    puntuaciones = {}
    for doc in documentos:
        texto = normalizar(doc["contenido"])
        puntuaciones[doc["archivo"]] = sum(1 for token in tokens if token in texto)
    mejor = max(documentos, key=lambda d: puntuaciones[d["archivo"]])
    return mejor, puntuaciones
