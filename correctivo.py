"""Registro y seguimiento de fallas de mantenimiento correctivo."""

from __future__ import annotations

import unicodedata
from datetime import datetime

from almacenamiento import cargar_lista, guardar_lista
from equipos import actualizar_datos_tecnicos, listar_equipos

ARCHIVO_CORRECTIVOS = "correctivos.json"
PRIORIDADES_CORRECTIVO = ("Baja", "Media", "Alta", "Crítica")
ESTADOS_CORRECTIVO = ("Reportado", "En revisión", "En reparación", "Resuelto", "Cancelado")
ESTADOS_CERRADOS = {"Resuelto", "Cancelado"}


def _normalizar_comparacion(valor: object) -> str:
    texto = unicodedata.normalize("NFKD", str(valor).strip().lower())
    return "".join(letra for letra in texto if not unicodedata.combining(letra))


def cargar_correctivos() -> list[dict]:
    return cargar_lista(ARCHIVO_CORRECTIVOS)


def guardar_correctivos(lista_correctivos: list[dict]) -> None:
    guardar_lista(ARCHIVO_CORRECTIVOS, lista_correctivos)


def validar_texto_correctivo(valor: object, nombre_campo: str) -> tuple[bool, str]:
    if not isinstance(valor, str):
        return False, f"El campo {nombre_campo} debe ser texto."
    if valor.strip() == "":
        return False, f"El campo {nombre_campo} no puede estar vacío."
    return True, ""


def validar_fecha_correctivo(fecha: object, nombre_campo: str) -> tuple[bool, str]:
    es_valido, mensaje = validar_texto_correctivo(fecha, nombre_campo)
    if not es_valido:
        return False, mensaje
    try:
        convertida = datetime.strptime(str(fecha).strip(), "%Y-%m-%d")
    except ValueError:
        return False, f"El campo {nombre_campo} debe tener el formato AAAA-MM-DD."
    if str(fecha).strip() != convertida.strftime("%Y-%m-%d"):
        return False, f"El campo {nombre_campo} debe tener el formato AAAA-MM-DD."
    return True, ""


def validar_fecha_opcional_correctivo(fecha: object, nombre_campo: str) -> tuple[bool, str]:
    if fecha is None or (isinstance(fecha, str) and fecha.strip() == ""):
        return True, ""
    return validar_fecha_correctivo(fecha, nombre_campo)


def _prioridad_canonica(prioridad: object) -> str | None:
    normalizado = _normalizar_comparacion(prioridad)
    return {
        "baja": "Baja",
        "media": "Media",
        "alta": "Alta",
        "critica": "Crítica",
    }.get(normalizado)


def validar_prioridad_correctivo(prioridad: object) -> tuple[bool, str]:
    es_valido, mensaje = validar_texto_correctivo(prioridad, "prioridad")
    if not es_valido:
        return False, mensaje
    if _prioridad_canonica(prioridad) is None:
        return False, "La prioridad debe ser Baja, Media, Alta o Crítica."
    return True, ""


def _estado_canonico(estado: object) -> str | None:
    normalizado = _normalizar_comparacion(estado)
    return {
        "reportado": "Reportado",
        "en revision": "En revisión",
        "en reparacion": "En reparación",
        "resuelto": "Resuelto",
        "cancelado": "Cancelado",
    }.get(normalizado)


def validar_estado_correctivo(estado: object) -> tuple[bool, str]:
    es_valido, mensaje = validar_texto_correctivo(estado, "estado")
    if not es_valido:
        return False, mensaje
    if _estado_canonico(estado) is None:
        return False, "El estado debe ser Reportado, En revisión, En reparación, Resuelto o Cancelado."
    return True, ""


def existe_equipo(lista_equipos: list[dict], codigo_equipo: object) -> bool:
    if not isinstance(codigo_equipo, str) or not codigo_equipo.strip():
        return False
    codigo = codigo_equipo.strip().upper()
    return any(str(equipo.get("codigo", "")).upper() == codigo for equipo in lista_equipos)


def existe_codigo_correctivo(lista_correctivos: list[dict], codigo_correctivo: object) -> bool:
    if not isinstance(codigo_correctivo, str) or not codigo_correctivo.strip():
        return False
    codigo = codigo_correctivo.strip().upper()
    return any(str(item.get("codigo_correctivo", "")).upper() == codigo for item in lista_correctivos)


def _generar_codigo_correctivo(lista_correctivos: list[dict]) -> str:
    mayor = 0
    for correctivo in lista_correctivos:
        codigo = str(correctivo.get("codigo_correctivo", "")).upper()
        if codigo.startswith("MC-") and codigo[3:].isdigit():
            mayor = max(mayor, int(codigo[3:]))
    return f"MC-{mayor + 1:04d}"


def crear_correctivo(
    codigo_correctivo: object,
    codigo_equipo: object,
    fecha_reporte: object,
    descripcion: object,
    prioridad: object,
    responsable: object,
    estado: object,
    fecha_solucion: object = None,
) -> dict:
    """Crea un registro ya validado, sin fallar cuando la fecha es opcional."""
    solucion = None if fecha_solucion is None or str(fecha_solucion).strip() == "" else str(fecha_solucion).strip()
    return {
        "codigo_correctivo": str(codigo_correctivo).strip().upper(),
        "codigo_equipo": str(codigo_equipo).strip().upper(),
        "fecha_reporte": str(fecha_reporte).strip(),
        "descripcion": str(descripcion).strip(),
        "prioridad": _prioridad_canonica(prioridad),
        "responsable": str(responsable).strip(),
        "estado": _estado_canonico(estado),
        "fecha_solucion": solucion,
    }


def validar_datos_correctivo(
    lista_equipos: list[dict],
    codigo_correctivo: object,
    codigo_equipo: object,
    fecha_reporte: object,
    descripcion: object,
    prioridad: object,
    responsable: object,
    estado: object,
    fecha_solucion: object = None,
) -> tuple[bool, str]:
    campos = {
        "código correctivo": codigo_correctivo,
        "código de equipo": codigo_equipo,
        "descripción": descripcion,
        "responsable": responsable,
    }
    for nombre, valor in campos.items():
        es_valido, mensaje = validar_texto_correctivo(valor, nombre)
        if not es_valido:
            return False, mensaje

    if not existe_equipo(lista_equipos, codigo_equipo):
        return False, "No existe un equipo registrado con ese código."

    for funcion, valor, nombre in (
        (validar_fecha_correctivo, fecha_reporte, "fecha de reporte"),
        (validar_prioridad_correctivo, prioridad, "prioridad"),
        (validar_estado_correctivo, estado, "estado"),
        (validar_fecha_opcional_correctivo, fecha_solucion, "fecha de solución"),
    ):
        es_valido, mensaje = funcion(valor, nombre) if funcion in {validar_fecha_correctivo, validar_fecha_opcional_correctivo} else funcion(valor)
        if not es_valido:
            return False, mensaje

    estado_validado = _estado_canonico(estado)
    solucion = None if fecha_solucion is None or str(fecha_solucion).strip() == "" else str(fecha_solucion).strip()
    if estado_validado == "Resuelto" and solucion is None:
        return False, "Un correctivo resuelto debe tener fecha de solución."
    if solucion is not None and str(solucion) < str(fecha_reporte).strip():
        return False, "La fecha de solución no puede ser anterior a la fecha de reporte."
    return True, ""


def _sincronizar_estado_equipo(codigo_equipo: str) -> None:
    correctivos = cargar_correctivos()
    hay_correctivo = any(
        str(item.get("codigo_equipo", "")).upper() == codigo_equipo.upper()
        and item.get("estado") not in ESTADOS_CERRADOS
        for item in correctivos
    )
    preventivos = cargar_lista("mantenimientos.json")
    hay_preventivo = any(
        str(item.get("codigo_equipo", "")).upper() == codigo_equipo.upper()
        and item.get("estado") == "En proceso"
        for item in preventivos
    )
    if hay_correctivo:
        estado = "Fuera de servicio"
    elif hay_preventivo:
        estado = "En mantenimiento"
    else:
        estado = "Operativo"
    actualizar_datos_tecnicos(codigo_equipo, estado=estado)


def registrar_correctivo(
    lista_correctivos: list[dict],
    lista_equipos: list[dict],
    codigo_correctivo: object,
    codigo_equipo: object,
    fecha_reporte: object,
    descripcion: object,
    prioridad: object,
    responsable: object,
    estado: object = "Reportado",
    fecha_solucion: object = None,
) -> tuple[bool, str]:
    """Registra un correctivo y sincroniza el estado del equipo."""
    if codigo_correctivo is None or str(codigo_correctivo).strip() == "":
        codigo_correctivo = _generar_codigo_correctivo(lista_correctivos)

    es_valido, mensaje = validar_datos_correctivo(
        lista_equipos,
        codigo_correctivo,
        codigo_equipo,
        fecha_reporte,
        descripcion,
        prioridad,
        responsable,
        estado,
        fecha_solucion,
    )
    if not es_valido:
        return False, mensaje
    if existe_codigo_correctivo(lista_correctivos, codigo_correctivo):
        return False, "Ya existe un correctivo registrado con ese código."

    nuevo = crear_correctivo(
        codigo_correctivo,
        codigo_equipo,
        fecha_reporte,
        descripcion,
        prioridad,
        responsable,
        estado,
        fecha_solucion,
    )
    lista_correctivos.append(nuevo)
    guardar_correctivos(lista_correctivos)
    _sincronizar_estado_equipo(nuevo["codigo_equipo"])
    return True, f"Correctivo {nuevo['codigo_correctivo']} registrado correctamente."


def listar_correctivos(lista_correctivos: list[dict]) -> list[dict]:
    return lista_correctivos


def buscar_correctivo_por_codigo(lista_correctivos: list[dict], codigo_correctivo: object) -> dict | None:
    if not isinstance(codigo_correctivo, str):
        return None
    codigo = codigo_correctivo.strip().upper()
    for correctivo in lista_correctivos:
        if str(correctivo.get("codigo_correctivo", "")).upper() == codigo:
            return correctivo
    return None


def listar_correctivos_por_equipo(lista_correctivos: list[dict], codigo_equipo: object) -> list[dict]:
    if not isinstance(codigo_equipo, str):
        return []
    codigo = codigo_equipo.strip().upper()
    return [item for item in lista_correctivos if str(item.get("codigo_equipo", "")).upper() == codigo]


def listar_correctivos_pendientes(lista_correctivos: list[dict]) -> list[dict]:
    return [item for item in lista_correctivos if item.get("estado") not in ESTADOS_CERRADOS]


def cambiar_estado_correctivo(
    lista_correctivos: list[dict],
    codigo_correctivo: object,
    nuevo_estado: object,
    fecha_solucion: object = None,
) -> tuple[bool, str]:
    es_valido, mensaje = validar_estado_correctivo(nuevo_estado)
    if not es_valido:
        return False, mensaje
    correctivo = buscar_correctivo_por_codigo(lista_correctivos, codigo_correctivo)
    if correctivo is None:
        return False, "No existe un correctivo registrado con ese código."

    estado = _estado_canonico(nuevo_estado)
    if estado == "Resuelto":
        solucion = datetime.now().strftime("%Y-%m-%d") if fecha_solucion in (None, "") else str(fecha_solucion).strip()
        es_fecha_valida, mensaje_fecha = validar_fecha_correctivo(solucion, "fecha de solución")
        if not es_fecha_valida:
            return False, mensaje_fecha
        if solucion < str(correctivo.get("fecha_reporte", "")):
            return False, "La fecha de solución no puede ser anterior a la fecha de reporte."
        correctivo["fecha_solucion"] = solucion
    else:
        correctivo["fecha_solucion"] = None

    correctivo["estado"] = estado
    guardar_correctivos(lista_correctivos)
    _sincronizar_estado_equipo(str(correctivo.get("codigo_equipo", "")))
    return True, "Estado del correctivo actualizado correctamente."


def _mostrar_correctivo(correctivo: dict) -> None:
    campos = (
        ("Código correctivo", "codigo_correctivo"),
        ("Código de equipo", "codigo_equipo"),
        ("Fecha de reporte", "fecha_reporte"),
        ("Descripción", "descripcion"),
        ("Prioridad", "prioridad"),
        ("Responsable", "responsable"),
        ("Estado", "estado"),
        ("Fecha de solución", "fecha_solucion"),
    )
    for etiqueta, campo in campos:
        print(f"{etiqueta}: {correctivo.get(campo, '')}")


def menu_correctivo() -> None:
    while True:
        print("\n--- MENÚ DE MANTENIMIENTO CORRECTIVO ---")
        print("1. Registrar falla")
        print("2. Buscar correctivo")
        print("3. Listar todos")
        print("4. Listar por equipo")
        print("5. Listar pendientes")
        print("6. Cambiar estado")
        print("7. Volver")
        opcion = input("Seleccione una opción: ").strip()
        try:
            correctivos = cargar_correctivos()
            if opcion == "1":
                codigo = input("Código correctivo [automático]: ").strip()
                exito, mensaje = registrar_correctivo(
                    correctivos,
                    listar_equipos(),
                    codigo,
                    input("Código del equipo: ").strip(),
                    input("Fecha de reporte (AAAA-MM-DD): ").strip(),
                    input("Descripción de la falla: ").strip(),
                    input("Prioridad (Baja/Media/Alta/Crítica): ").strip(),
                    input("Responsable: ").strip(),
                    "Reportado",
                    None,
                )
                print(mensaje)
            elif opcion == "2":
                encontrado = buscar_correctivo_por_codigo(correctivos, input("Código correctivo: ").strip())
                if encontrado:
                    _mostrar_correctivo(encontrado)
                else:
                    print("No se encontró el correctivo.")
            elif opcion == "3":
                if not correctivos:
                    print("No hay correctivos registrados.")
                for indice, item in enumerate(correctivos, 1):
                    print(f"\nCorrectivo {indice}")
                    _mostrar_correctivo(item)
            elif opcion == "4":
                lista = listar_correctivos_por_equipo(correctivos, input("Código del equipo: ").strip())
                if not lista:
                    print("No hay correctivos para ese equipo.")
                for item in lista:
                    print()
                    _mostrar_correctivo(item)
            elif opcion == "5":
                lista = listar_correctivos_pendientes(correctivos)
                if not lista:
                    print("No hay correctivos pendientes.")
                for item in lista:
                    print()
                    _mostrar_correctivo(item)
            elif opcion == "6":
                codigo = input("Código correctivo: ").strip()
                estado = input("Nuevo estado: ").strip()
                fecha = input("Fecha de solución [hoy si se resuelve]: ").strip()
                _, mensaje = cambiar_estado_correctivo(correctivos, codigo, estado, fecha or None)
                print(mensaje)
            elif opcion == "7":
                break
            else:
                print("Opción no válida.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu_correctivo()



