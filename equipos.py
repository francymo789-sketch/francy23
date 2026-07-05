"""Registro, búsqueda y actualización de maquinaria pesada."""

from __future__ import annotations

import math
import unicodedata

from almacenamiento import cargar_lista, guardar_lista

ARCHIVO_EQUIPOS = "maquinaria.json"
ESTADOS_EQUIPO = ("Operativo", "En mantenimiento", "Fuera de servicio")


def _normalizar_comparacion(valor: object) -> str:
    texto = unicodedata.normalize("NFKD", str(valor).strip().lower())
    return "".join(letra for letra in texto if not unicodedata.combining(letra))


def _cargar_equipos() -> list[dict]:
    return cargar_lista(ARCHIVO_EQUIPOS)


def _guardar_equipos(equipos: list[dict]) -> None:
    guardar_lista(ARCHIVO_EQUIPOS, equipos)


def _validar_texto_obligatorio(valor: object, nombre_campo: str) -> str:
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"El campo {nombre_campo} es obligatorio.")
    return str(valor).strip()


def _validar_texto_opcional(valor: object, nombre_campo: str) -> str | None:
    if valor is None:
        return None
    return _validar_texto_obligatorio(valor, nombre_campo)


def _validar_horas_uso(horas_uso: object) -> float:
    if isinstance(horas_uso, bool):
        raise ValueError("Las horas de uso deben ser un valor numérico.")
    try:
        horas = float(horas_uso)
    except (TypeError, ValueError) as error:
        raise ValueError("Las horas de uso deben ser un valor numérico.") from error
    if not math.isfinite(horas):
        raise ValueError("Las horas de uso deben ser un número finito.")
    if horas < 0:
        raise ValueError("Las horas de uso no pueden ser negativas.")
    return horas


def _normalizar_codigo(codigo: object) -> str:
    return _validar_texto_obligatorio(codigo, "código").upper()


def _validar_estado(estado: object) -> str:
    estado_texto = _validar_texto_obligatorio(estado, "estado")
    normalizado = _normalizar_comparacion(estado_texto)
    alias = {
        "operativo": "Operativo",
        "en mantenimiento": "En mantenimiento",
        "en mantenimiento preventivo": "En mantenimiento",
        "en reparacion": "En mantenimiento",
        "fuera de servicio": "Fuera de servicio",
    }
    if normalizado not in alias:
        permitidos = ", ".join(ESTADOS_EQUIPO)
        raise ValueError(f"El estado debe ser uno de estos: {permitidos}.")
    return alias[normalizado]


def registrar_equipo(
    codigo: object,
    nombre: object,
    modelo: object,
    horas_uso: object,
    area_asignada: object,
    estado: object = "Operativo",
) -> dict:
    """Registra un equipo nuevo y devuelve el registro creado."""
    lista = _cargar_equipos()
    codigo_normalizado = _normalizar_codigo(codigo)
    if any(str(item.get("codigo", "")).upper() == codigo_normalizado for item in lista):
        raise ValueError(f"Ya existe un equipo con el código {codigo_normalizado}.")

    equipo = {
        "codigo": codigo_normalizado,
        "nombre": _validar_texto_obligatorio(nombre, "nombre"),
        "modelo": _validar_texto_obligatorio(modelo, "modelo"),
        "horas_uso": _validar_horas_uso(horas_uso),
        "area_asignada": _validar_texto_obligatorio(area_asignada, "área asignada"),
        "estado": _validar_estado(estado),
    }
    lista.append(equipo)
    _guardar_equipos(lista)
    return equipo


def buscar_equipo(codigo: object) -> dict | None:
    codigo_normalizado = _normalizar_codigo(codigo)
    for equipo in _cargar_equipos():
        if str(equipo.get("codigo", "")).upper() == codigo_normalizado:
            return equipo
    return None


def actualizar_datos_tecnicos(
    codigo: object,
    horas_uso: object = None,
    modelo: object = None,
    area_asignada: object = None,
    estado: object = None,
) -> dict:
    """Actualiza únicamente los campos enviados para un equipo existente."""
    codigo_normalizado = _normalizar_codigo(codigo)
    lista = _cargar_equipos()

    for equipo in lista:
        if str(equipo.get("codigo", "")).upper() != codigo_normalizado:
            continue
        if horas_uso is not None:
            equipo["horas_uso"] = _validar_horas_uso(horas_uso)
        if modelo is not None:
            equipo["modelo"] = _validar_texto_opcional(modelo, "modelo")
        if area_asignada is not None:
            equipo["area_asignada"] = _validar_texto_opcional(area_asignada, "área asignada")
        if estado is not None:
            equipo["estado"] = _validar_estado(estado)
        _guardar_equipos(lista)
        return equipo

    raise ValueError(f"No existe un equipo con el código {codigo_normalizado}.")


def listar_equipos() -> list[dict]:
    return _cargar_equipos()


def _pedir_campo(mensaje: str) -> str:
    return input(mensaje).strip()


def _mostrar_equipo(equipo: dict) -> None:
    print(f"Código: {equipo.get('codigo', 'N/A')}")
    print(f"Nombre: {equipo.get('nombre', 'N/A')}")
    print(f"Modelo: {equipo.get('modelo', 'N/A')}")
    print(f"Horas de uso: {equipo.get('horas_uso', 0)}")
    print(f"Área asignada: {equipo.get('area_asignada', 'N/A')}")
    print(f"Estado: {equipo.get('estado', 'N/A')}")


def menu_equipos() -> None:
    while True:
        print("\n--- MENÚ DE EQUIPOS ---")
        print("1. Registrar equipo")
        print("2. Buscar equipo por código")
        print("3. Actualizar datos técnicos")
        print("4. Listar equipos")
        print("5. Volver")
        opcion = _pedir_campo("Seleccione una opción: ")

        try:
            if opcion == "1":
                equipo = registrar_equipo(
                    _pedir_campo("Código: "),
                    _pedir_campo("Nombre: "),
                    _pedir_campo("Modelo: "),
                    _pedir_campo("Horas de uso: "),
                    _pedir_campo("Área asignada: "),
                    _pedir_campo("Estado [Operativo]: ") or "Operativo",
                )
                print("\nEquipo registrado correctamente.")
                _mostrar_equipo(equipo)
            elif opcion == "2":
                equipo = buscar_equipo(_pedir_campo("Código a buscar: "))
                if equipo:
                    _mostrar_equipo(equipo)
                else:
                    print("No se encontró un equipo con ese código.")
            elif opcion == "3":
                codigo = _pedir_campo("Código del equipo: ")
                horas = _pedir_campo("Nuevas horas [Enter para mantener]: ")
                modelo = _pedir_campo("Nuevo modelo [Enter para mantener]: ")
                area = _pedir_campo("Nueva área [Enter para mantener]: ")
                estado = _pedir_campo("Nuevo estado [Enter para mantener]: ")
                equipo = actualizar_datos_tecnicos(
                    codigo,
                    horas if horas else None,
                    modelo if modelo else None,
                    area if area else None,
                    estado if estado else None,
                )
                print("\nEquipo actualizado correctamente.")
                _mostrar_equipo(equipo)
            elif opcion == "4":
                lista = listar_equipos()
                if not lista:
                    print("No hay equipos registrados.")
                for indice, equipo in enumerate(lista, 1):
                    print(f"\nEquipo {indice}")
                    _mostrar_equipo(equipo)
            elif opcion == "5":
                break
            else:
                print("Opción no válida.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu_equipos()
