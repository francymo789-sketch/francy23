"""Control de inventario de repuestos para maquinaria pesada."""

from __future__ import annotations

import math
import unicodedata

from almacenamiento import cargar_lista, guardar_lista

ARCHIVO_STOCK = "stock.json"
CATEGORIAS_REPUESTO = (
    "Motor",
    "Hidráulico",
    "Eléctrico",
    "Transmisión",
    "Frenos",
    "Filtros",
    "Neumáticos",
    "Lubricantes",
    "Otro",
)


def _normalizar_comparacion(valor: object) -> str:
    texto = unicodedata.normalize("NFKD", str(valor).strip().lower())
    return "".join(letra for letra in texto if not unicodedata.combining(letra))


def cargar_stock() -> list[dict]:
    return cargar_lista(ARCHIVO_STOCK)


def guardar_stock(lista_stock: list[dict]) -> None:
    guardar_lista(ARCHIVO_STOCK, lista_stock)


def validar_texto_stock(valor: object, nombre_campo: str) -> tuple[bool, str]:
    if not isinstance(valor, str):
        return False, f"El campo {nombre_campo} debe ser texto."
    if valor.strip() == "":
        return False, f"El campo {nombre_campo} no puede estar vacío."
    return True, ""


def validar_entero_stock(valor: object, nombre_campo: str) -> tuple[bool, str]:
    if isinstance(valor, bool):
        return False, f"El campo {nombre_campo} debe ser un número entero."
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return False, f"El campo {nombre_campo} debe ser un número entero."
    if isinstance(valor, float) and not valor.is_integer():
        return False, f"El campo {nombre_campo} debe ser un número entero."
    if numero < 0:
        return False, f"El campo {nombre_campo} no puede ser negativo."
    return True, ""


def validar_precio_stock(precio_unitario: object) -> tuple[bool, str]:
    if isinstance(precio_unitario, bool):
        return False, "El precio unitario debe ser numérico."
    try:
        precio = float(precio_unitario)
    except (TypeError, ValueError):
        return False, "El precio unitario debe ser numérico."
    if not math.isfinite(precio):
        return False, "El precio unitario debe ser un número finito."
    if precio < 0:
        return False, "El precio unitario no puede ser negativo."
    return True, ""


def _categoria_canonica(categoria: object) -> str | None:
    normalizado = _normalizar_comparacion(categoria)
    for permitida in CATEGORIAS_REPUESTO:
        if _normalizar_comparacion(permitida) == normalizado:
            return permitida
    return None


def validar_categoria_stock(categoria: object) -> tuple[bool, str]:
    es_valido, mensaje = validar_texto_stock(categoria, "categoría")
    if not es_valido:
        return False, mensaje
    if _categoria_canonica(categoria) is None:
        return False, "La categoría del repuesto no es válida."
    return True, ""


def existe_codigo_repuesto(lista_stock: list[dict], codigo_repuesto: object) -> bool:
    if not isinstance(codigo_repuesto, str) or not codigo_repuesto.strip():
        return False
    codigo = codigo_repuesto.strip().upper()
    return any(str(item.get("codigo_repuesto", "")).upper() == codigo for item in lista_stock)


def crear_repuesto(
    codigo_repuesto: object,
    nombre: object,
    categoria: object,
    marca: object,
    modelo_compatible: object,
    cantidad: object,
    stock_minimo: object,
    precio_unitario: object,
    proveedor: object,
) -> dict:
    return {
        "codigo_repuesto": str(codigo_repuesto).strip().upper(),
        "nombre": str(nombre).strip(),
        "categoria": _categoria_canonica(categoria),
        "marca": str(marca).strip(),
        "modelo_compatible": str(modelo_compatible).strip(),
        "cantidad": int(cantidad),
        "stock_minimo": int(stock_minimo),
        "precio_unitario": float(precio_unitario),
        "proveedor": str(proveedor).strip(),
    }


def validar_datos_repuesto(
    codigo_repuesto: object,
    nombre: object,
    categoria: object,
    marca: object,
    modelo_compatible: object,
    cantidad: object,
    stock_minimo: object,
    precio_unitario: object,
    proveedor: object,
) -> tuple[bool, str]:
    for nombre_campo, valor in {
        "código de repuesto": codigo_repuesto,
        "nombre": nombre,
        "categoría": categoria,
        "marca": marca,
        "modelo compatible": modelo_compatible,
        "proveedor": proveedor,
    }.items():
        es_valido, mensaje = validar_texto_stock(valor, nombre_campo)
        if not es_valido:
            return False, mensaje

    for funcion, valor, nombre_campo in (
        (validar_entero_stock, cantidad, "cantidad"),
        (validar_entero_stock, stock_minimo, "stock mínimo"),
    ):
        es_valido, mensaje = funcion(valor, nombre_campo)
        if not es_valido:
            return False, mensaje

    es_valido, mensaje = validar_categoria_stock(categoria)
    if not es_valido:
        return False, mensaje
    es_valido, mensaje = validar_precio_stock(precio_unitario)
    if not es_valido:
        return False, mensaje
    return True, ""


def registrar_repuesto(
    lista_stock: list[dict],
    codigo_repuesto: object,
    nombre: object,
    categoria: object,
    marca: object,
    modelo_compatible: object,
    cantidad: object,
    stock_minimo: object,
    precio_unitario: object,
    proveedor: object,
) -> tuple[bool, str]:
    es_valido, mensaje = validar_datos_repuesto(
        codigo_repuesto,
        nombre,
        categoria,
        marca,
        modelo_compatible,
        cantidad,
        stock_minimo,
        precio_unitario,
        proveedor,
    )
    if not es_valido:
        return False, mensaje
    if existe_codigo_repuesto(lista_stock, codigo_repuesto):
        return False, "Ya existe un repuesto registrado con ese código."

    nuevo = crear_repuesto(
        codigo_repuesto,
        nombre,
        categoria,
        marca,
        modelo_compatible,
        cantidad,
        stock_minimo,
        precio_unitario,
        proveedor,
    )
    lista_stock.append(nuevo)
    guardar_stock(lista_stock)
    return True, "Repuesto registrado correctamente."


def listar_stock(lista_stock: list[dict]) -> list[dict]:
    return lista_stock


def buscar_repuesto_por_codigo(lista_stock: list[dict], codigo_repuesto: object) -> dict | None:
    if not isinstance(codigo_repuesto, str):
        return None
    codigo = codigo_repuesto.strip().upper()
    for repuesto in lista_stock:
        if str(repuesto.get("codigo_repuesto", "")).upper() == codigo:
            return repuesto
    return None


def actualizar_stock(
    lista_stock: list[dict],
    codigo_repuesto: object,
    cantidad_movimiento: object,
) -> tuple[bool, str]:
    repuesto = buscar_repuesto_por_codigo(lista_stock, codigo_repuesto)
    if repuesto is None:
        return False, "No existe un repuesto registrado con ese código."
    if isinstance(cantidad_movimiento, bool):
        return False, "La cantidad de movimiento debe ser un número entero."
    try:
        movimiento = int(cantidad_movimiento)
    except (TypeError, ValueError):
        return False, "La cantidad de movimiento debe ser un número entero."
    if isinstance(cantidad_movimiento, float) and not cantidad_movimiento.is_integer():
        return False, "La cantidad de movimiento debe ser un número entero."

    actual = int(repuesto.get("cantidad", 0))
    nuevo_stock = actual + movimiento
    if nuevo_stock < 0:
        return False, "El stock no puede quedar en negativo."
    repuesto["cantidad"] = nuevo_stock
    guardar_stock(lista_stock)
    return True, "Stock actualizado correctamente."


def listar_repuestos_bajo_stock(lista_stock: list[dict]) -> list[dict]:
    return [
        item
        for item in lista_stock
        if int(item.get("cantidad", 0)) <= int(item.get("stock_minimo", 0))
    ]


def calcular_valor_total_stock(lista_stock: list[dict]) -> float:
    return sum(
        int(item.get("cantidad", 0)) * float(item.get("precio_unitario", 0))
        for item in lista_stock
    )


def _mostrar_repuesto(repuesto: dict) -> None:
    campos = (
        ("Código", "codigo_repuesto"),
        ("Nombre", "nombre"),
        ("Categoría", "categoria"),
        ("Marca", "marca"),
        ("Modelo compatible", "modelo_compatible"),
        ("Cantidad", "cantidad"),
        ("Stock mínimo", "stock_minimo"),
        ("Precio unitario", "precio_unitario"),
        ("Proveedor", "proveedor"),
    )
    for etiqueta, campo in campos:
        print(f"{etiqueta}: {repuesto.get(campo, '')}")


def menu_stock() -> None:
    while True:
        print("\n--- MENÚ DE STOCK DE REPUESTOS ---")
        print("1. Registrar repuesto")
        print("2. Buscar repuesto")
        print("3. Listar inventario")
        print("4. Registrar entrada o salida")
        print("5. Ver repuestos con stock bajo")
        print("6. Ver valor total del inventario")
        print("7. Volver")
        opcion = input("Seleccione una opción: ").strip()
        try:
            lista = cargar_stock()
            if opcion == "1":
                print("Categorías: " + ", ".join(CATEGORIAS_REPUESTO))
                exito, mensaje = registrar_repuesto(
                    lista,
                    input("Código: ").strip(),
                    input("Nombre: ").strip(),
                    input("Categoría: ").strip(),
                    input("Marca: ").strip(),
                    input("Modelo compatible: ").strip(),
                    input("Cantidad inicial: ").strip(),
                    input("Stock mínimo: ").strip(),
                    input("Precio unitario: ").strip(),
                    input("Proveedor: ").strip(),
                )
                print(mensaje)
            elif opcion == "2":
                repuesto = buscar_repuesto_por_codigo(lista, input("Código: ").strip())
                if repuesto:
                    _mostrar_repuesto(repuesto)
                else:
                    print("No se encontró el repuesto.")
            elif opcion == "3":
                if not lista:
                    print("No hay repuestos registrados.")
                for indice, repuesto in enumerate(lista, 1):
                    print(f"\nRepuesto {indice}")
                    _mostrar_repuesto(repuesto)
            elif opcion == "4":
                print("Use una cantidad positiva para entrada y negativa para salida.")
                _, mensaje = actualizar_stock(
                    lista,
                    input("Código: ").strip(),
                    input("Cantidad del movimiento: ").strip(),
                )
                print(mensaje)
            elif opcion == "5":
                bajos = listar_repuestos_bajo_stock(lista)
                if not bajos:
                    print("No hay repuestos con stock bajo.")
                for repuesto in bajos:
                    print()
                    _mostrar_repuesto(repuesto)
            elif opcion == "6":
                print(f"Valor total del inventario: S/ {calcular_valor_total_stock(lista):,.2f}")
            elif opcion == "7":
                break
            else:
                print("Opción no válida.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu_stock()
