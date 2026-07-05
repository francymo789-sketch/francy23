
ARCHIVO_STOCK = "stock.json"

CATEGORIAS_REPUESTO = [
    "Motor",
    "Hidráulico",
    "Eléctrico",
    "Transmisión",
    "Frenos",
    "Filtros",
    "Neumáticos",
    "Lubricantes",
    "Otro"
]

def cargar_stock():
    """Carga la lista de repuestos desde un archivo JSON."""
    if not os.path.exists(ARCHIVO_STOCK):
        return []

    try:
        with open(ARCHIVO_STOCK, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

            if isinstance(datos, list):
                return datos

            return []

    except json.JSONDecodeError:
        return []


def guardar_stock(lista_stock):
    """Guarda la lista de repuestos en un archivo JSON."""
    with open(ARCHIVO_STOCK, "w", encoding="utf-8") as archivo:
        json.dump(lista_stock, archivo, indent=4, ensure_ascii=False)


def validar_texto_stock(valor, nombre_campo):
    """Valida que un campo obligatorio no esté vacío."""
    if not isinstance(valor, str):
        return False, f"El campo {nombre_campo} debe ser texto."

    if valor.strip() == "":
        return False, f"El campo {nombre_campo} no puede estar vacío."

    return True, ""


def validar_entero_stock(valor, nombre_campo):
    """Valida que un valor sea entero y no negativo."""
    try:
        numero = int(valor)

        if numero < 0:
            return False, f"El campo {nombre_campo} no puede ser negativo."

        return True, ""

    except ValueError:
        return False, f"El campo {nombre_campo} debe ser un número entero."


def validar_precio_stock(precio_unitario):
    """Valida que el precio unitario sea numérico y no negativo."""
    try:
        precio_convertido = float(precio_unitario)

        if precio_convertido < 0:
            return False, "El precio unitario no puede ser negativo."

        return True, ""

    except ValueError:
        return False, "El precio unitario debe ser numérico."


def validar_categoria_stock(categoria):
    """Valida que la categoría del repuesto esté permitida."""
    es_valido, mensaje = validar_texto_stock(categoria, "categoría")

    if not es_valido:
        return False, mensaje

    if categoria.strip() not in CATEGORIAS_REPUESTO:
        return False, "La categoría del repuesto no es válida."

    return True, ""


def existe_codigo_repuesto(lista_stock, codigo_repuesto):
    """Verifica si ya existe un repuesto con el mismo código."""
    for repuesto in lista_stock:
        if repuesto["codigo_repuesto"].lower() == codigo_repuesto.strip().lower():
            return True

    return False


def crear_repuesto(
    codigo_repuesto,
    nombre,
    categoria,
    marca,
    modelo_compatible,
    cantidad,
    stock_minimo,
    precio_unitario,
    proveedor
):
    """Crea un diccionario con los datos del repuesto."""
    repuesto = {
        "codigo_repuesto": codigo_repuesto.strip().upper(),
        "nombre": nombre.strip(),
        "categoria": categoria.strip(),
        "marca": marca.strip(),
        "modelo_compatible": modelo_compatible.strip(),
        "cantidad": int(cantidad),
        "stock_minimo": int(stock_minimo),
        "precio_unitario": float(precio_unitario),
        "proveedor": proveedor.strip()
    }

    return repuesto


def validar_datos_repuesto(
    codigo_repuesto,
    nombre,
    categoria,
    marca,
    modelo_compatible,
    cantidad,
    stock_minimo,
    precio_unitario,
    proveedor
):
    """Valida todos los datos antes de registrar un repuesto."""
    campos_texto = {
        "código de repuesto": codigo_repuesto,
        "nombre": nombre,
        "categoría": categoria,
        "marca": marca,
        "modelo compatible": modelo_compatible,
        "proveedor": proveedor
    }

    for nombre_campo, valor in campos_texto.items():
        es_valido, mensaje = validar_texto_stock(valor, nombre_campo)

        if not es_valido:
            return False, mensaje

    es_valido, mensaje = validar_categoria_stock(categoria)

    if not es_valido:
        return False, mensaje

    es_valido, mensaje = validar_entero_stock(cantidad, "cantidad")

    if not es_valido:
        return False, mensaje

    es_valido, mensaje = validar_entero_stock(stock_minimo, "stock mínimo")

    if not es_valido:
        return False, mensaje

    if int(stock_minimo) > int(cantidad):
        return False, "El stock mínimo no puede ser mayor que la cantidad inicial."

    es_valido, mensaje = validar_precio_stock(precio_unitario)

    if not es_valido:
        return False, mensaje

    return True, ""


def registrar_repuesto(
    lista_stock,
    codigo_repuesto,
    nombre,
    categoria,
    marca,
    modelo_compatible,
    cantidad,
    stock_minimo,
    precio_unitario,
    proveedor
):
    """Registra un repuesto nuevo en el inventario."""
    es_valido, mensaje = validar_datos_repuesto(
        codigo_repuesto,
        nombre,
        categoria,
        marca,
        modelo_compatible,
        cantidad,
        stock_minimo,
        precio_unitario,
        proveedor
    )

    if not es_valido:
        return False, mensaje

    if existe_codigo_repuesto(lista_stock, codigo_repuesto):
        return False, "Ya existe un repuesto registrado con ese código."

    nuevo_repuesto = crear_repuesto(
        codigo_repuesto,
        nombre,
        categoria,
        marca,
        modelo_compatible,
        cantidad,
        stock_minimo,
        precio_unitario,
        proveedor
    )

    lista_stock.append(nuevo_repuesto)
    guardar_stock(lista_stock)

    return True, "Repuesto registrado correctamente."


def listar_stock(lista_stock):
    """Devuelve la lista completa del inventario."""
    return lista_stock


def buscar_repuesto_por_codigo(lista_stock, codigo_repuesto):
    """Busca un repuesto por su código."""
    for repuesto in lista_stock:
        if repuesto["codigo_repuesto"].lower() == codigo_repuesto.strip().lower():
            return repuesto

    return None


def actualizar_stock(lista_stock, codigo_repuesto, cantidad_movimiento):
    """Actualiza el stock sumando o restando una cantidad."""
    repuesto = buscar_repuesto_por_codigo(lista_stock, codigo_repuesto)

    if repuesto is None:
        return False, "No existe un repuesto registrado con ese código."

    try:
        cantidad_convertida = int(cantidad_movimiento)

    except ValueError:
        return False, "La cantidad de movimiento debe ser un número entero."

    nuevo_stock = repuesto["cantidad"] + cantidad_convertida

    if nuevo_stock < 0:
        return False, "El stock no puede quedar en negativo."

    repuesto["cantidad"] = nuevo_stock
    guardar_stock(lista_stock)

    return True, "Stock actualizado correctamente."


def listar_repuestos_bajo_stock(lista_stock):
    """Lista repuestos que están en stock mínimo o por debajo."""
    repuestos_bajo_stock = []

    for repuesto in lista_stock:
        if repuesto["cantidad"] <= repuesto["stock_minimo"]:
            repuestos_bajo_stock.append(repuesto)

    return repuestos_bajo_stock


def calcular_valor_total_stock(lista_stock):
    """Calcula el valor económico total del inventario."""
    valor_total = 0

    for repuesto in lista_stock:
        valor_total += repuesto["cantidad"] * repuesto["precio_unitario"]

    return valor_total
def contar_total_equipos(lista_equipos):
    """Cuenta el total de equipos registrados."""
    return len(lista_equipos)


def contar_equipos_por_estado(lista_equipos, estado):
    """Cuenta equipos según su estado."""
    total = 0

    for equipo in lista_equipos:
        if equipo["estado"] == estado:
            total += 1

    return total


def contar_total_preventivos(lista_preventivos):
    """Cuenta el total de mantenimientos preventivos."""
    return len(lista_preventivos)


def contar_preventivos_por_estado(lista_preventivos, estado):
    """Cuenta preventivos según su estado."""
    total = 0

    for preventivo in lista_preventivos:
        if preventivo["estado"] == estado:
            total += 1

    return total


def calcular_costo_total_preventivos(lista_preventivos):
    """Calcula el costo total de mantenimientos preventivos."""
    costo_total = 0

    for preventivo in lista_preventivos:
        costo_total += preventivo["costo"]

    return costo_total


def contar_total_correctivos(lista_correctivos):
    """Cuenta el total de fallas o tickets correctivos."""
    return len(lista_correctivos)


def contar_correctivos_por_estado(lista_correctivos, estado):
    """Cuenta correctivos según su estado."""
    total = 0

    for correctivo in lista_correctivos:
        if correctivo["estado"] == estado:
            total += 1

    return total


def contar_correctivos_por_prioridad(lista_correctivos, prioridad):
    """Cuenta correctivos según su prioridad."""
    total = 0

    for correctivo in lista_correctivos:
        if correctivo["prioridad"] == prioridad:
            total += 1

    return total


def contar_total_repuestos(lista_stock):
    """Cuenta el total de repuestos registrados."""
    return len(lista_stock)


def contar_repuestos_bajo_stock(lista_stock):
    """Cuenta repuestos con stock mínimo o por debajo."""
    total = 0

    for repuesto in lista_stock:
        if repuesto["cantidad"] <= repuesto["stock_minimo"]:
            total += 1

    return total


def calcular_valor_total_stock(lista_stock):
    """Calcula el valor económico total del inventario."""
    valor_total = 0

    for repuesto in lista_stock:
        valor_total += repuesto["cantidad"] * repuesto["precio_unitario"]

    return valor_total


def generar_reporte_general(
    lista_equipos,
    lista_preventivos,
    lista_correctivos,
    lista_stock
):
    """Genera un reporte general del sistema."""
    reporte = {
        "total_equipos": contar_total_equipos(lista_equipos),
        "equipos_operativos": contar_equipos_por_estado(lista_equipos, "Operativo"),
        "equipos_en_mantenimiento": contar_equipos_por_estado(lista_equipos, "En mantenimiento"),
        "equipos_fuera_servicio": contar_equipos_por_estado(lista_equipos, "Fuera de servicio"),
        "total_preventivos": contar_total_preventivos(lista_preventivos),
        "preventivos_programados": contar_preventivos_por_estado(lista_preventivos, "Programado"),
        "preventivos_en_proceso": contar_preventivos_por_estado(lista_preventivos, "En proceso"),
        "preventivos_finalizados": contar_preventivos_por_estado(lista_preventivos, "Finalizado"),
        "preventivos_cancelados": contar_preventivos_por_estado(lista_preventivos, "Cancelado"),
        "costo_total_preventivos": calcular_costo_total_preventivos(lista_preventivos),
        "total_correctivos": contar_total_correctivos(lista_correctivos),
        "correctivos_reportados": contar_correctivos_por_estado(lista_correctivos, "Reportado"),
        "correctivos_en_revision": contar_correctivos_por_estado(lista_correctivos, "En revisión"),
        "correctivos_en_reparacion": contar_correctivos_por_estado(lista_correctivos, "En reparación"),
        "correctivos_resueltos": contar_correctivos_por_estado(lista_correctivos, "Resuelto"),
        "correctivos_cancelados": contar_correctivos_por_estado(lista_correctivos, "Cancelado"),
        "correctivos_criticos": contar_correctivos_por_prioridad(lista_correctivos, "Crítica"),
        "total_repuestos": contar_total_repuestos(lista_stock),
        "repuestos_bajo_stock": contar_repuestos_bajo_stock(lista_stock),
        "valor_total_stock": calcular_valor_total_stock(lista_stock)
    }


