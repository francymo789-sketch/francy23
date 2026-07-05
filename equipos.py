"""Modulo para registrar, consultar y actualizar maquinaria pesada."""

import json
from pathlib import Path


RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_DATOS = RUTA_BASE / "datos"
RUTA_ARCHIVO = RUTA_DATOS / "maquinaria.json"


def _crear_archivo_si_no_existe():
    """Crea el archivo JSON vacio si todavia no existe."""
    RUTA_DATOS.mkdir(parents=True, exist_ok=True)

    if not RUTA_ARCHIVO.exists():
        RUTA_ARCHIVO.write_text("[]", encoding="utf-8")


def _cargar_equipos():
    """Carga los equipos guardados y maneja errores de lectura del JSON."""
    # El archivo se prepara solo cuando alguna funcion necesita usarlo.
    _crear_archivo_si_no_existe()

    try:
        contenido = RUTA_ARCHIVO.read_text(encoding="utf-8").strip()
        if not contenido:
            return []

        equipos = json.loads(contenido)
        if not isinstance(equipos, list):
            raise ValueError("El archivo de maquinaria debe contener una lista.")

        return equipos
    except json.JSONDecodeError as error:
        raise ValueError("No se pudo leer maquinaria.json: el JSON no es valido.") from error
    except OSError as error:
        raise ValueError("No se pudo leer el archivo de maquinaria.") from error


def _guardar_equipos(equipos):
    """Guarda la lista de equipos en formato JSON con codificacion UTF-8."""
    _crear_archivo_si_no_existe()

    try:
        # ensure_ascii=False conserva correctamente tildes y caracteres en espanol.
        texto_json = json.dumps(equipos, ensure_ascii=False, indent=4)
        RUTA_ARCHIVO.write_text(texto_json, encoding="utf-8")
    except OSError as error:
        raise ValueError("No se pudo guardar el archivo de maquinaria.") from error


def _validar_texto_obligatorio(valor, nombre_campo):
    """Valida que un campo de texto obligatorio tenga contenido."""
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"El campo {nombre_campo} es obligatorio.")

    return str(valor).strip()


def _validar_texto_opcional(valor, nombre_campo):
    """Valida un campo de texto opcional cuando se envia un valor."""
    if valor is None:
        return None

    return _validar_texto_obligatorio(valor, nombre_campo)


def _validar_horas_uso(horas_uso):
    """Valida que las horas de uso sean numericas y no negativas."""
    try:
        horas = float(horas_uso)
    except (TypeError, ValueError) as error:
        raise ValueError("Las horas de uso deben ser un valor numerico.") from error

    if horas < 0:
        raise ValueError("Las horas de uso no pueden ser negativas.")

    return horas


def _normalizar_codigo(codigo):
    """Valida y convierte el codigo del equipo a mayusculas."""
    codigo_validado = _validar_texto_obligatorio(codigo, "codigo")
    return codigo_validado.upper()


def registrar_equipo(
    codigo,
    nombre,
    modelo,
    horas_uso,
    area_asignada,
    estado="Operativo"
):
    """Registra un equipo nuevo y lo guarda en maquinaria.json."""
    equipos = _cargar_equipos()
    codigo_normalizado = _normalizar_codigo(codigo)

    if any(equipo.get("codigo", "").upper() == codigo_normalizado for equipo in equipos):
        raise ValueError(f"Ya existe un equipo con el codigo {codigo_normalizado}.")

    equipo = {
        "codigo": codigo_normalizado,
        "nombre": _validar_texto_obligatorio(nombre, "nombre"),
        "modelo": _validar_texto_obligatorio(modelo, "modelo"),
        "horas_uso": _validar_horas_uso(horas_uso),
        "area_asignada": _validar_texto_obligatorio(area_asignada, "area_asignada"),
        "estado": _validar_texto_obligatorio(estado, "estado"),
    }

    equipos.append(equipo)
    _guardar_equipos(equipos)
    return equipo


def buscar_equipo(codigo):
    """Busca un equipo por codigo sin distinguir mayusculas y minusculas."""
    codigo_normalizado = _normalizar_codigo(codigo)
    equipos = _cargar_equipos()

    for equipo in equipos:
        if equipo.get("codigo", "").upper() == codigo_normalizado:
            return equipo

    return None


def actualizar_datos_tecnicos(
    codigo,
    horas_uso=None,
    modelo=None,
    area_asignada=None,
    estado=None
):
    """Actualiza los datos tecnicos indicados para un equipo existente."""
    codigo_normalizado = _normalizar_codigo(codigo)
    equipos = _cargar_equipos()

    for equipo in equipos:
        if equipo.get("codigo", "").upper() == codigo_normalizado:
            # Solo se cambian los valores enviados; None mantiene el dato anterior.
            if horas_uso is not None:
                equipo["horas_uso"] = _validar_horas_uso(horas_uso)

            modelo_validado = _validar_texto_opcional(modelo, "modelo")
            area_validada = _validar_texto_opcional(area_asignada, "area_asignada")
            estado_validado = _validar_texto_opcional(estado, "estado")

            if modelo_validado is not None:
                equipo["modelo"] = modelo_validado
            if area_validada is not None:
                equipo["area_asignada"] = area_validada
            if estado_validado is not None:
                equipo["estado"] = estado_validado

            _guardar_equipos(equipos)
            return equipo

    raise ValueError(f"No existe un equipo con el codigo {codigo_normalizado}.")


def listar_equipos():
    """Retorna todos los equipos registrados."""
    return _cargar_equipos()


def _pedir_campo(mensaje):
    """Solicita un dato por consola y elimina espacios sobrantes."""
    return input(mensaje).strip()


def _mostrar_equipo(equipo):
    """Muestra un equipo en consola de forma legible."""
    print(f"Codigo: {equipo['codigo']}")
    print(f"Nombre: {equipo['nombre']}")
    print(f"Modelo: {equipo['modelo']}")
    print(f"Horas de uso: {equipo['horas_uso']}")
    print(f"Area asignada: {equipo['area_asignada']}")
    print(f"Estado: {equipo['estado']}")


def menu_equipos():
    """Menu de prueba para gestionar equipos desde la consola."""
    while True:
        print("\n--- Menu de equipos ---")
        print("1. Registrar equipo")
        print("2. Buscar equipo por codigo")
        print("3. Actualizar datos tecnicos")
        print("4. Listar equipos")
        print("5. Salir o volver")

        opcion = _pedir_campo("Seleccione una opcion: ")

        try:
            if opcion == "1":
                equipo = registrar_equipo(
                    codigo=_pedir_campo("Codigo: "),
                    nombre=_pedir_campo("Nombre: "),
                    modelo=_pedir_campo("Modelo: "),
                    horas_uso=_pedir_campo("Horas de uso: "),
                    area_asignada=_pedir_campo("Area asignada: "),
                    estado=_pedir_campo("Estado [Operativo]: ") or "Operativo",
                )
                print("\nEquipo registrado correctamente:")
                _mostrar_equipo(equipo)

            elif opcion == "2":
                equipo = buscar_equipo(_pedir_campo("Codigo a buscar: "))
                if equipo is None:
                    print("No se encontro un equipo con ese codigo.")
                else:
                    _mostrar_equipo(equipo)

            elif opcion == "3":
                codigo = _pedir_campo("Codigo del equipo: ")
                horas = _pedir_campo("Nuevas horas de uso [Enter para mantener]: ")
                modelo = _pedir_campo("Nuevo modelo [Enter para mantener]: ")
                area = _pedir_campo("Nueva area asignada [Enter para mantener]: ")
                estado = _pedir_campo("Nuevo estado [Enter para mantener]: ")

                equipo = actualizar_datos_tecnicos(
                    codigo=codigo,
                    horas_uso=horas if horas else None,
                    modelo=modelo if modelo else None,
                    area_asignada=area if area else None,
                    estado=estado if estado else None,
                )
                print("\nEquipo actualizado correctamente:")
                _mostrar_equipo(equipo)

            elif opcion == "4":
                equipos = listar_equipos()
                if not equipos:
                    print("No hay equipos registrados.")
                else:
                    for indice, equipo in enumerate(equipos, start=1):
                        print(f"\nEquipo {indice}")
                        _mostrar_equipo(equipo)

            elif opcion == "5":
                print("Volviendo al menu anterior.")
                break

            else:
                print("Opcion no valida.")

        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu_equipos()
