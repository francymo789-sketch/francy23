"""Modulo para administrar mantenimientos preventivos de maquinaria."""

import json
from datetime import datetime
from pathlib import Path

try:
    from modulos.equipos import buscar_equipo, actualizar_datos_tecnicos
except ModuleNotFoundError:
    from equipos import buscar_equipo, actualizar_datos_tecnicos


ESTADO_PROGRAMADO = "Programado"
ESTADO_EN_PROCESO = "En proceso"
ESTADO_COMPLETADO = "Completado"
ESTADOS_PERMITIDOS = (ESTADO_PROGRAMADO, ESTADO_EN_PROCESO, ESTADO_COMPLETADO)

RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_DATOS = RUTA_BASE / "datos"
RUTA_ARCHIVO = RUTA_DATOS / "mantenimientos.json"


def _crear_archivo_si_no_existe():
    """Crea el archivo JSON de mantenimientos si todavia no existe."""
    RUTA_DATOS.mkdir(parents=True, exist_ok=True)

    if not RUTA_ARCHIVO.exists():
        RUTA_ARCHIVO.write_text("[]", encoding="utf-8")


def _cargar_mantenimientos():
    """Carga los mantenimientos guardados y valida la estructura del JSON."""
    _crear_archivo_si_no_existe()

    try:
        contenido = RUTA_ARCHIVO.read_text(encoding="utf-8").strip()
        if not contenido:
            return []

        mantenimientos = json.loads(contenido)
        if not isinstance(mantenimientos, list):
            raise ValueError("El archivo de mantenimientos debe contener una lista.")

        return mantenimientos
    except json.JSONDecodeError as error:
        raise ValueError("No se pudo leer mantenimientos.json: el JSON no es valido.") from error
    except OSError as error:
        raise ValueError("No se pudo leer el archivo de mantenimientos.") from error


def _guardar_mantenimientos(mantenimientos):
    """Guarda la lista de mantenimientos con codificacion UTF-8."""
    _crear_archivo_si_no_existe()

    try:
        texto_json = json.dumps(mantenimientos, ensure_ascii=False, indent=4)
        RUTA_ARCHIVO.write_text(texto_json, encoding="utf-8")
    except OSError as error:
        raise ValueError("No se pudo guardar el archivo de mantenimientos.") from error


def _validar_texto_obligatorio(valor, nombre_campo):
    """Valida que un campo obligatorio tenga contenido."""
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"El campo {nombre_campo} es obligatorio.")

    return str(valor).strip()


def _normalizar_codigo(codigo, nombre_campo):
    """Valida y convierte un codigo a mayusculas."""
    return _validar_texto_obligatorio(codigo, nombre_campo).upper()


def _validar_fecha(fecha):
    """Valida una fecha en formato AAAA-MM-DD."""
    fecha_validada = _validar_texto_obligatorio(fecha, "fecha")

    try:
        fecha_convertida = datetime.strptime(fecha_validada, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from error

    if fecha_validada != fecha_convertida.strftime("%Y-%m-%d"):
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.")

    return fecha_validada


def _validar_estado(estado):
    """Valida que el estado pertenezca a los estados permitidos."""
    estado_validado = _validar_texto_obligatorio(estado, "estado")

    for estado_permitido in ESTADOS_PERMITIDOS:
        if estado_validado.lower() == estado_permitido.lower():
            return estado_permitido

    raise ValueError("El estado debe ser Programado, En proceso o Completado.")


def _generar_codigo_mantenimiento(mantenimientos):
    """Genera un codigo correlativo unico para mantenimiento preventivo."""
    numero_mayor = 0

    for mantenimiento in mantenimientos:
        codigo = str(mantenimiento.get("codigo_mantenimiento", "")).upper()
        if codigo.startswith("MP-") and codigo[3:].isdigit():
            numero_mayor = max(numero_mayor, int(codigo[3:]))

    return f"MP-{numero_mayor + 1:04d}"


def programar_mantenimiento(
    codigo_equipo,
    fecha_programada,
    tipo_servicio,
    descripcion,
    responsable=""
):
    """Programa un mantenimiento preventivo para un equipo existente."""
    codigo_equipo_validado = _normalizar_codigo(codigo_equipo, "codigo_equipo")

    if buscar_equipo(codigo_equipo_validado) is None:
        raise ValueError(f"No existe un equipo con el codigo {codigo_equipo_validado}.")

    mantenimientos = _cargar_mantenimientos()
    mantenimiento = {
        "codigo_mantenimiento": _generar_codigo_mantenimiento(mantenimientos),
        "codigo_equipo": codigo_equipo_validado,
        "fecha_programada": _validar_fecha(fecha_programada),
        "tipo_servicio": _validar_texto_obligatorio(tipo_servicio, "tipo_servicio"),
        "descripcion": _validar_texto_obligatorio(descripcion, "descripcion"),
        "responsable": "" if responsable is None else str(responsable).strip(),
        "estado": ESTADO_PROGRAMADO,
        "fecha_realizada": None,
        "observaciones": "",
    }

    mantenimientos.append(mantenimiento)
    _guardar_mantenimientos(mantenimientos)
    return mantenimiento


def buscar_mantenimiento(codigo_mantenimiento):
    """Busca un mantenimiento por codigo sin distinguir mayusculas."""
    codigo_validado = _normalizar_codigo(codigo_mantenimiento, "codigo_mantenimiento")
    mantenimientos = _cargar_mantenimientos()

    for mantenimiento in mantenimientos:
        codigo_actual = str(mantenimiento.get("codigo_mantenimiento", "")).upper()
        if codigo_actual == codigo_validado:
            return mantenimiento

    return None


def listar_mantenimientos(codigo_equipo=None, estado=None):
    """Lista mantenimientos con filtros opcionales por equipo y estado."""
    mantenimientos = _cargar_mantenimientos()
    codigo_equipo_validado = None
    estado_validado = None

    if codigo_equipo is not None:
        codigo_equipo_validado = _normalizar_codigo(codigo_equipo, "codigo_equipo")
    if estado is not None:
        estado_validado = _validar_estado(estado)

    resultado = []
    for mantenimiento in mantenimientos:
        if codigo_equipo_validado is not None:
            codigo_actual = str(mantenimiento.get("codigo_equipo", "")).upper()
            if codigo_actual != codigo_equipo_validado:
                continue

        if estado_validado is not None and mantenimiento.get("estado") != estado_validado:
            continue

        resultado.append(mantenimiento)

    return resultado


def iniciar_mantenimiento(codigo_mantenimiento):
    """Inicia un mantenimiento programado y cambia el estado del equipo."""
    codigo_validado = _normalizar_codigo(codigo_mantenimiento, "codigo_mantenimiento")
    mantenimientos = _cargar_mantenimientos()

    for mantenimiento in mantenimientos:
        codigo_actual = str(mantenimiento.get("codigo_mantenimiento", "")).upper()
        if codigo_actual == codigo_validado:
            if mantenimiento.get("estado") != ESTADO_PROGRAMADO:
                raise ValueError("Solo se pueden iniciar mantenimientos con estado Programado.")

            mantenimiento["estado"] = ESTADO_EN_PROCESO
            actualizar_datos_tecnicos(
                codigo=mantenimiento["codigo_equipo"],
                estado="En mantenimiento preventivo"
            )
            _guardar_mantenimientos(mantenimientos)
            return mantenimiento

    raise ValueError(f"No existe un mantenimiento con el codigo {codigo_validado}.")


def finalizar_mantenimiento(
    codigo_mantenimiento,
    fecha_realizada=None,
    observaciones=""
):
    """Finaliza un mantenimiento en proceso y deja el equipo operativo."""
    codigo_validado = _normalizar_codigo(codigo_mantenimiento, "codigo_mantenimiento")
    mantenimientos = _cargar_mantenimientos()

    for mantenimiento in mantenimientos:
        codigo_actual = str(mantenimiento.get("codigo_mantenimiento", "")).upper()
        if codigo_actual == codigo_validado:
            if mantenimiento.get("estado") != ESTADO_EN_PROCESO:
                raise ValueError("Solo se pueden finalizar mantenimientos con estado En proceso.")

            fecha_final = (
                datetime.now().strftime("%Y-%m-%d")
                if fecha_realizada is None
                else _validar_fecha(fecha_realizada)
            )

            mantenimiento["estado"] = ESTADO_COMPLETADO
            mantenimiento["fecha_realizada"] = fecha_final
            mantenimiento["observaciones"] = "" if observaciones is None else str(observaciones).strip()
            actualizar_datos_tecnicos(
                codigo=mantenimiento["codigo_equipo"],
                estado="Operativo"
            )
            _guardar_mantenimientos(mantenimientos)
            return mantenimiento

    raise ValueError(f"No existe un mantenimiento con el codigo {codigo_validado}.")


def _pedir_campo(mensaje):
    """Solicita un dato por consola y elimina espacios sobrantes."""
    return input(mensaje).strip()


def _mostrar_mantenimiento(mantenimiento):
    """Muestra los datos de un mantenimiento en consola."""
    print(f"Codigo de mantenimiento: {mantenimiento['codigo_mantenimiento']}")
    print(f"Codigo de equipo: {mantenimiento['codigo_equipo']}")
    print(f"Fecha programada: {mantenimiento['fecha_programada']}")
    print(f"Tipo de servicio: {mantenimiento['tipo_servicio']}")
    print(f"Descripcion: {mantenimiento['descripcion']}")
    print(f"Responsable: {mantenimiento['responsable']}")
    print(f"Estado: {mantenimiento['estado']}")
    print(f"Fecha realizada: {mantenimiento['fecha_realizada']}")
    print(f"Observaciones: {mantenimiento['observaciones']}")


def menu_preventivo():
    """Menu de prueba para administrar mantenimientos preventivos."""
    while True:
        print("\n--- Menu de mantenimiento preventivo ---")
        print("1. Programar mantenimiento preventivo")
        print("2. Buscar mantenimiento")
        print("3. Listar mantenimientos")
        print("4. Iniciar mantenimiento")
        print("5. Finalizar mantenimiento")
        print("6. Salir o volver")

        opcion = _pedir_campo("Seleccione una opcion: ")

        try:
            if opcion == "1":
                mantenimiento = programar_mantenimiento(
                    codigo_equipo=_pedir_campo("Codigo del equipo: "),
                    fecha_programada=_pedir_campo("Fecha programada (AAAA-MM-DD): "),
                    tipo_servicio=_pedir_campo("Tipo de servicio: "),
                    descripcion=_pedir_campo("Descripcion: "),
                    responsable=_pedir_campo("Responsable [opcional]: "),
                )
                print("\nMantenimiento programado correctamente:")
                _mostrar_mantenimiento(mantenimiento)

            elif opcion == "2":
                mantenimiento = buscar_mantenimiento(
                    _pedir_campo("Codigo del mantenimiento: ")
                )
                if mantenimiento is None:
                    print("No se encontro un mantenimiento con ese codigo.")
                else:
                    _mostrar_mantenimiento(mantenimiento)

            elif opcion == "3":
                codigo_equipo = _pedir_campo("Codigo de equipo [Enter para todos]: ")
                estado = _pedir_campo("Estado [Enter para todos]: ")
                mantenimientos = listar_mantenimientos(
                    codigo_equipo=codigo_equipo if codigo_equipo else None,
                    estado=estado if estado else None,
                )

                if not mantenimientos:
                    print("No hay mantenimientos para mostrar.")
                else:
                    for indice, mantenimiento in enumerate(mantenimientos, start=1):
                        print(f"\nMantenimiento {indice}")
                        _mostrar_mantenimiento(mantenimiento)

            elif opcion == "4":
                mantenimiento = iniciar_mantenimiento(
                    _pedir_campo("Codigo del mantenimiento: ")
                )
                print("\nMantenimiento iniciado correctamente:")
                _mostrar_mantenimiento(mantenimiento)

            elif opcion == "5":
                fecha = _pedir_campo("Fecha realizada (AAAA-MM-DD) [Enter para hoy]: ")
                mantenimiento = finalizar_mantenimiento(
                    codigo_mantenimiento=_pedir_campo("Codigo del mantenimiento: "),
                    fecha_realizada=fecha if fecha else None,
                    observaciones=_pedir_campo("Observaciones [opcional]: "),
                )
                print("\nMantenimiento finalizado correctamente:")
                _mostrar_mantenimiento(mantenimiento)

            elif opcion == "6":
                print("Volviendo al menu anterior.")
                break

            else:
                print("Opcion no valida.")

        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu_preventivo()
