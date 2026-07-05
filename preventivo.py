"""Programación y seguimiento del mantenimiento preventivo."""

from __future__ import annotations

import math
import unicodedata
from datetime import datetime

from almacenamiento import cargar_lista, guardar_lista
from equipos import actualizar_datos_tecnicos, buscar_equipo

ARCHIVO_PREVENTIVOS = "mantenimientos.json"
ESTADO_PROGRAMADO = "Programado"
ESTADO_EN_PROCESO = "En proceso"
ESTADO_COMPLETADO = "Completado"
ESTADO_CANCELADO = "Cancelado"
ESTADOS_PERMITIDOS = (
    ESTADO_PROGRAMADO,
    ESTADO_EN_PROCESO,
    ESTADO_COMPLETADO,
    ESTADO_CANCELADO,
)


def _normalizar_comparacion(valor: object) -> str:
    texto = unicodedata.normalize("NFKD", str(valor).strip().lower())
    return "".join(letra for letra in texto if not unicodedata.combining(letra))


def _cargar_mantenimientos() -> list[dict]:
    return cargar_lista(ARCHIVO_PREVENTIVOS)


def _guardar_mantenimientos(mantenimientos: list[dict]) -> None:
    guardar_lista(ARCHIVO_PREVENTIVOS, mantenimientos)


def _validar_texto_obligatorio(valor: object, nombre_campo: str) -> str:
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"El campo {nombre_campo} es obligatorio.")
    return str(valor).strip()


def _normalizar_codigo(codigo: object, nombre_campo: str) -> str:
    return _validar_texto_obligatorio(codigo, nombre_campo).upper()


def _validar_fecha(fecha: object) -> str:
    texto = _validar_texto_obligatorio(fecha, "fecha")
    try:
        convertida = datetime.strptime(texto, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from error
    if texto != convertida.strftime("%Y-%m-%d"):
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.")
    return texto


def _validar_costo(costo: object) -> float:
    if costo in (None, ""):
        return 0.0
    if isinstance(costo, bool):
        raise ValueError("El costo debe ser numérico.")
    try:
        numero = float(costo)
    except (TypeError, ValueError) as error:
        raise ValueError("El costo debe ser numérico.") from error
    if not math.isfinite(numero) or numero < 0:
        raise ValueError("El costo debe ser un número finito mayor o igual que cero.")
    return numero


def _validar_estado(estado: object) -> str:
    normalizado = _normalizar_comparacion(_validar_texto_obligatorio(estado, "estado"))
    equivalencias = {
        "programado": ESTADO_PROGRAMADO,
        "en proceso": ESTADO_EN_PROCESO,
        "completado": ESTADO_COMPLETADO,
        "finalizado": ESTADO_COMPLETADO,
        "cancelado": ESTADO_CANCELADO,
    }
    if normalizado not in equivalencias:
        raise ValueError("El estado debe ser Programado, En proceso, Completado o Cancelado.")
    return equivalencias[normalizado]


def _generar_codigo_mantenimiento(mantenimientos: list[dict]) -> str:
    mayor = 0
    for mantenimiento in mantenimientos:
        codigo = str(mantenimiento.get("codigo_mantenimiento", "")).upper()
        if codigo.startswith("MP-") and codigo[3:].isdigit():
            mayor = max(mayor, int(codigo[3:]))
    return f"MP-{mayor + 1:04d}"


def programar_mantenimiento(
    codigo_equipo: object,
    fecha_programada: object,
    tipo_servicio: object,
    descripcion: object,
    responsable: object = "",
    costo: object = 0,
) -> dict:
    """Programa un mantenimiento para un equipo existente."""
    codigo_equipo_validado = _normalizar_codigo(codigo_equipo, "código de equipo")
    if buscar_equipo(codigo_equipo_validado) is None:
        raise ValueError(f"No existe un equipo con el código {codigo_equipo_validado}.")

    mantenimientos = _cargar_mantenimientos()
    mantenimiento = {
        "codigo_mantenimiento": _generar_codigo_mantenimiento(mantenimientos),
        "codigo_equipo": codigo_equipo_validado,
        "fecha_programada": _validar_fecha(fecha_programada),
        "tipo_servicio": _validar_texto_obligatorio(tipo_servicio, "tipo de servicio"),
        "descripcion": _validar_texto_obligatorio(descripcion, "descripción"),
        "responsable": "" if responsable is None else str(responsable).strip(),
        "estado": ESTADO_PROGRAMADO,
        "fecha_realizada": None,
        "observaciones": "",
        "costo": _validar_costo(costo),
    }
    mantenimientos.append(mantenimiento)
    _guardar_mantenimientos(mantenimientos)
    return mantenimiento


def buscar_mantenimiento(codigo_mantenimiento: object) -> dict | None:
    codigo = _normalizar_codigo(codigo_mantenimiento, "código de mantenimiento")
    for mantenimiento in _cargar_mantenimientos():
        if str(mantenimiento.get("codigo_mantenimiento", "")).upper() == codigo:
            return mantenimiento
    return None


def listar_mantenimientos(codigo_equipo: object = None, estado: object = None) -> list[dict]:
    codigo = None if codigo_equipo is None else _normalizar_codigo(codigo_equipo, "código de equipo")
    estado_validado = None if estado is None else _validar_estado(estado)
    resultado = []
    for mantenimiento in _cargar_mantenimientos():
        if codigo is not None and str(mantenimiento.get("codigo_equipo", "")).upper() != codigo:
            continue
        if estado_validado is not None and mantenimiento.get("estado") != estado_validado:
            continue
        resultado.append(mantenimiento)
    return resultado


def _hay_correctivo_abierto(codigo_equipo: str) -> bool:
    estados_cerrados = {"Resuelto", "Cancelado"}
    for correctivo in cargar_lista("correctivos.json"):
        if str(correctivo.get("codigo_equipo", "")).upper() == codigo_equipo.upper():
            if correctivo.get("estado") not in estados_cerrados:
                return True
    return False


def _sincronizar_estado_equipo(codigo_equipo: str) -> None:
    mantenimientos = _cargar_mantenimientos()
    en_proceso = any(
        str(item.get("codigo_equipo", "")).upper() == codigo_equipo.upper()
        and item.get("estado") == ESTADO_EN_PROCESO
        for item in mantenimientos
    )
    if _hay_correctivo_abierto(codigo_equipo):
        estado = "Fuera de servicio"
    elif en_proceso:
        estado = "En mantenimiento"
    else:
        estado = "Operativo"
    actualizar_datos_tecnicos(codigo_equipo, estado=estado)


def iniciar_mantenimiento(codigo_mantenimiento: object) -> dict:
    codigo = _normalizar_codigo(codigo_mantenimiento, "código de mantenimiento")
    mantenimientos = _cargar_mantenimientos()
    for mantenimiento in mantenimientos:
        if str(mantenimiento.get("codigo_mantenimiento", "")).upper() != codigo:
            continue
        if mantenimiento.get("estado") != ESTADO_PROGRAMADO:
            raise ValueError("Solo se pueden iniciar mantenimientos con estado Programado.")
        equipo = mantenimiento.get("codigo_equipo", "")
        otro_activo = any(
            item is not mantenimiento
            and str(item.get("codigo_equipo", "")).upper() == str(equipo).upper()
            and item.get("estado") == ESTADO_EN_PROCESO
            for item in mantenimientos
        )
        if otro_activo:
            raise ValueError("El equipo ya tiene otro mantenimiento preventivo en proceso.")
        mantenimiento["estado"] = ESTADO_EN_PROCESO
        _guardar_mantenimientos(mantenimientos)
        _sincronizar_estado_equipo(str(equipo))
        return mantenimiento
    raise ValueError(f"No existe un mantenimiento con el código {codigo}.")


def finalizar_mantenimiento(
    codigo_mantenimiento: object,
    fecha_realizada: object = None,
    observaciones: object = "",
    costo: object = None,
) -> dict:
    codigo = _normalizar_codigo(codigo_mantenimiento, "código de mantenimiento")
    mantenimientos = _cargar_mantenimientos()
    for mantenimiento in mantenimientos:
        if str(mantenimiento.get("codigo_mantenimiento", "")).upper() != codigo:
            continue
        if mantenimiento.get("estado") != ESTADO_EN_PROCESO:
            raise ValueError("Solo se pueden finalizar mantenimientos con estado En proceso.")

        fecha_final = datetime.now().strftime("%Y-%m-%d") if fecha_realizada in (None, "") else _validar_fecha(fecha_realizada)
        fecha_programada = _validar_fecha(mantenimiento.get("fecha_programada"))
        if fecha_final < fecha_programada:
            raise ValueError("La fecha realizada no puede ser anterior a la fecha programada.")

        mantenimiento["estado"] = ESTADO_COMPLETADO
        mantenimiento["fecha_realizada"] = fecha_final
        mantenimiento["observaciones"] = "" if observaciones is None else str(observaciones).strip()
        if costo is not None:
            mantenimiento["costo"] = _validar_costo(costo)
        else:
            mantenimiento["costo"] = _validar_costo(mantenimiento.get("costo", 0))
        _guardar_mantenimientos(mantenimientos)
        _sincronizar_estado_equipo(str(mantenimiento.get("codigo_equipo", "")))
        return mantenimiento
    raise ValueError(f"No existe un mantenimiento con el código {codigo}.")


def cancelar_mantenimiento(codigo_mantenimiento: object, motivo: object = "") -> dict:
    codigo = _normalizar_codigo(codigo_mantenimiento, "código de mantenimiento")
    mantenimientos = _cargar_mantenimientos()
    for mantenimiento in mantenimientos:
        if str(mantenimiento.get("codigo_mantenimiento", "")).upper() != codigo:
            continue
        if mantenimiento.get("estado") in {ESTADO_COMPLETADO, ESTADO_CANCELADO}:
            raise ValueError("No se puede cancelar un mantenimiento completado o ya cancelado.")
        mantenimiento["estado"] = ESTADO_CANCELADO
        mantenimiento["observaciones"] = "" if motivo is None else str(motivo).strip()
        _guardar_mantenimientos(mantenimientos)
        _sincronizar_estado_equipo(str(mantenimiento.get("codigo_equipo", "")))
        return mantenimiento
    raise ValueError(f"No existe un mantenimiento con el código {codigo}.")


def _mostrar_mantenimiento(mantenimiento: dict) -> None:
    etiquetas = (
        ("Código de mantenimiento", "codigo_mantenimiento"),
        ("Código de equipo", "codigo_equipo"),
        ("Fecha programada", "fecha_programada"),
        ("Tipo de servicio", "tipo_servicio"),
        ("Descripción", "descripcion"),
        ("Responsable", "responsable"),
        ("Estado", "estado"),
        ("Fecha realizada", "fecha_realizada"),
        ("Observaciones", "observaciones"),
        ("Costo", "costo"),
    )
    for etiqueta, campo in etiquetas:
        print(f"{etiqueta}: {mantenimiento.get(campo, '')}")


def menu_preventivo() -> None:
    while True:
        print("\n--- MENÚ DE MANTENIMIENTO PREVENTIVO ---")
        print("1. Programar mantenimiento")
        print("2. Buscar mantenimiento")
        print("3. Listar mantenimientos")
        print("4. Iniciar mantenimiento")
        print("5. Finalizar mantenimiento")
        print("6. Cancelar mantenimiento")
        print("7. Volver")
        opcion = input("Seleccione una opción: ").strip()
        try:
            if opcion == "1":
                mantenimiento = programar_mantenimiento(
                    input("Código del equipo: ").strip(),
                    input("Fecha programada (AAAA-MM-DD): ").strip(),
                    input("Tipo de servicio: ").strip(),
                    input("Descripción: ").strip(),
                    input("Responsable [opcional]: ").strip(),
                    input("Costo estimado [0]: ").strip() or 0,
                )
                print("\nMantenimiento programado correctamente.")
                _mostrar_mantenimiento(mantenimiento)
            elif opcion == "2":
                mantenimiento = buscar_mantenimiento(input("Código del mantenimiento: ").strip())
                if mantenimiento:
                    _mostrar_mantenimiento(mantenimiento)
                else:
                    print("No se encontró el mantenimiento.")
            elif opcion == "3":
                equipo = input("Código de equipo [Enter para todos]: ").strip()
                estado = input("Estado [Enter para todos]: ").strip()
                lista = listar_mantenimientos(equipo or None, estado or None)
                if not lista:
                    print("No hay mantenimientos para mostrar.")
                for indice, mantenimiento in enumerate(lista, 1):
                    print(f"\nMantenimiento {indice}")
                    _mostrar_mantenimiento(mantenimiento)
            elif opcion == "4":
                mantenimiento = iniciar_mantenimiento(input("Código del mantenimiento: ").strip())
                print("Mantenimiento iniciado correctamente.")
                _mostrar_mantenimiento(mantenimiento)
            elif opcion == "5":
                codigo = input("Código del mantenimiento: ").strip()
                fecha = input("Fecha realizada (AAAA-MM-DD) [hoy]: ").strip()
                observaciones = input("Observaciones [opcional]: ").strip()
                costo = input("Costo final [mantener]: ").strip()
                mantenimiento = finalizar_mantenimiento(codigo, fecha or None, observaciones, costo if costo else None)
                print("Mantenimiento finalizado correctamente.")
                _mostrar_mantenimiento(mantenimiento)
            elif opcion == "6":
                mantenimiento = cancelar_mantenimiento(
                    input("Código del mantenimiento: ").strip(),
                    input("Motivo [opcional]: ").strip(),
                )
                print("Mantenimiento cancelado correctamente.")
                _mostrar_mantenimiento(mantenimiento)
            elif opcion == "7":
                break
            else:
                print("Opción no válida.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu_preventivo()
