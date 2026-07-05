import json
import os

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


# =====================================================================
# MENÚ INTERACTIVO AÑADIDO PARA LA INTEGRACIÓN
# =====================================================================
def menu_stock():
    lista_stock = cargar_stock()
    
    while True:
        print("\n" + "-"*40)
        print(" GESTIÓN DE STOCK DE REPUESTOS")
        print("-" * 40)
        print("1. Registrar nuevo repuesto")
        print("2. Mostrar inventario completo")
        print("3. Actualizar cantidad de stock")
        print("4. Ver repuestos con stock bajo")
        print("5. Volver al Menú Principal")
        
        opcion = input("\nSeleccione una opción (1-5): ")
        
        if opcion == '1':
            print("\n--- Registro de Repuesto ---")
            codigo = input("Código de repuesto: ")
            nombre = input("Nombre de repuesto: ")
            print(f"Categorías válidas: {', '.join(CATEGORIAS_REPUESTO)}")
            categoria = input("Categoría: ")
            marca = input("Marca: ")
            modelo = input("Modelo compatible: ")
            cantidad = input("Cantidad inicial: ")
            minimo = input("Stock mínimo: ")
            precio = input("Precio unitario: ")
            proveedor = input("Proveedor: ")
            
            exito, msj = registrar_repuesto(
                lista_stock, codigo, nombre, categoria, marca, 
                modelo, cantidad, minimo, precio, proveedor
            )
            print(f"\n[{'EXITO' if exito else 'ERROR'}] {msj}")
            
        elif opcion == '2':
            inventario = listar_stock(lista_stock)
            print("\n--- Inventario Actual ---")
            if not inventario:
                print("El inventario está vacío.")
            else:
                for rep in inventario:
                    print(f"[{rep['codigo_repuesto']}] {rep['nombre']} - Cantidad: {rep['cantidad']} - Precio: ${rep['precio_unitario']}")
                    
        elif opcion == '3':
            print("\n--- Actualizar Stock ---")
            codigo = input("Ingrese el código del repuesto: ")
            cantidad = input("Cantidad a sumar (positiva) o restar (negativa): ")
            
            exito, msj = actualizar_stock(lista_stock, codigo, cantidad)
            print(f"\n[{'EXITO' if exito else 'ERROR'}] {msj}")
            
        elif opcion == '4':
            bajo_stock = listar_repuestos_bajo_stock(lista_stock)
            print("\n--- Repuestos en Nivel Crítico ---")
            if not bajo_stock:
                print("No hay repuestos por debajo del stock mínimo. Todo en orden.")
            else:
                for rep in bajo_stock:
                    print(f"[{rep['codigo_repuesto']}] {rep['nombre']} - Quedan: {rep['cantidad']} (Mínimo: {rep['stock_minimo']})")
                    
        elif opcion == '5':
            print("\nSaliendo del módulo de Stock...")
            break
            
        else:
            print("\n[!] Opción inválida. Intente de nuevo.")
