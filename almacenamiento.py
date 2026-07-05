"""Funciones compartidas para leer y guardar los archivos JSON del sistema."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("COMPU_DATA_DIR", BASE_DIR / "datos"))


def ruta_datos(nombre_archivo: str) -> Path:
    """Devuelve la ruta segura de un archivo dentro de la carpeta de datos."""
    nombre = Path(nombre_archivo).name
    if not nombre.endswith(".json"):
        raise ValueError("El archivo de datos debe tener extensión .json.")
    return DATA_DIR / nombre


def _migrar_archivo_antiguo(nombre_archivo: str, destino: Path) -> None:
    """Copia un JSON antiguo ubicado en la raíz, si existe y es válido."""
    origen = BASE_DIR / Path(nombre_archivo).name
    if not origen.exists() or origen == destino:
        return

    try:
        datos = json.loads(origen.read_text(encoding="utf-8") or "[]")
    except (OSError, json.JSONDecodeError):
        return

    if isinstance(datos, list):
        guardar_lista(nombre_archivo, datos)


def asegurar_archivo(nombre_archivo: str) -> Path:
    """Crea la carpeta y el archivo JSON cuando todavía no existen."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ruta = ruta_datos(nombre_archivo)
    if not ruta.exists():
        _migrar_archivo_antiguo(nombre_archivo, ruta)
    if not ruta.exists():
        ruta.write_text("[]\n", encoding="utf-8")
    return ruta


def cargar_lista(nombre_archivo: str) -> list[dict[str, Any]]:
    """Carga una lista de diccionarios desde un archivo JSON."""
    ruta = asegurar_archivo(nombre_archivo)
    try:
        contenido = ruta.read_text(encoding="utf-8").strip()
        datos = json.loads(contenido or "[]")
    except json.JSONDecodeError as error:
        raise ValueError(f"El archivo {ruta.name} contiene un JSON inválido.") from error
    except OSError as error:
        raise OSError(f"No se pudo leer el archivo {ruta.name}.") from error

    if not isinstance(datos, list):
        raise ValueError(f"El archivo {ruta.name} debe contener una lista JSON.")
    if not all(isinstance(registro, dict) for registro in datos):
        raise ValueError(f"Todos los registros de {ruta.name} deben ser objetos JSON.")
    return datos


def guardar_lista(nombre_archivo: str, datos: list[dict[str, Any]]) -> None:
    """Guarda una lista en JSON mediante reemplazo atómico."""
    if not isinstance(datos, list) or not all(isinstance(item, dict) for item in datos):
        raise ValueError("Los datos que se guardarán deben ser una lista de diccionarios.")

    ruta = ruta_datos(nombre_archivo)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    try:
        temporal.write_text(
            json.dumps(datos, ensure_ascii=False, indent=4) + "\n",
            encoding="utf-8",
        )
        temporal.replace(ruta)
    except OSError as error:
        try:
            temporal.unlink(missing_ok=True)
        except OSError:
            pass
        raise OSError(f"No se pudo guardar el archivo {ruta.name}.") from error
