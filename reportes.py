import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def cargar_json(nombre_archivo):
    ruta_archivo = BASE_DIR / nombre_archivo

    try:
        with ruta_archivo.open("r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def cargar_maquinaria():
    return cargar_json("maquinaria.json")


def cargar_mantenimientos():
    return cargar_json("mantenimientos.json")


def cargar_correctivos():
    return cargar_json("correctivos.json")


def cargar_stock():
    return cargar_json("stock.json")


def contar_por_estado(lista_datos, estados):
    conteos = {estado: 0 for estado in estados}

    for dato in lista_datos:
        estado = dato.get("estado")
        if estado in conteos:
            conteos[estado] += 1

    return conteos


def contar_por_campo(lista_datos, campo):
    conteos = {}

    for dato in lista_datos:
        valor = dato.get(campo)
        if valor:
            conteos[valor] = conteos.get(valor, 0) + 1

    return conteos


def obtener_numero(diccionario, claves):
    for clave in claves:
        valor = diccionario.get(clave)
        if isinstance(valor, (int, float)):
            return valor

        try:
            return float(valor)
        except (TypeError, ValueError):
            continue

    return 0


def generar_reporte_general(
    lista_equipos,
    lista_preventivos,
    lista_correctivos,
    lista_stock,
):
    estados_equipos = ["Operativo", "En mantenimiento", "Fuera de servicio"]
    reporte = {
        "total_equipos": len(lista_equipos),
        "equipos_por_estado": contar_por_estado(lista_equipos, estados_equipos),
        "preventivos_por_estado": contar_por_campo(lista_preventivos, "estado"),
        "costo_total_preventivos": 0,
        "correctivos_por_estado": contar_por_campo(lista_correctivos, "estado"),
        "correctivos_prioridad_critica": 0,
        "total_repuestos": len(lista_stock),
        "valor_total_stock": 0,
    }

    for preventivo in lista_preventivos:
        reporte["costo_total_preventivos"] += obtener_numero(
            preventivo,
            ["costo", "costo_total", "valor", "monto"],
        )

    for correctivo in lista_correctivos:
        if correctivo.get("prioridad") in ("Cr\u00edtica", "Critica"):
            reporte["correctivos_prioridad_critica"] += 1

    for repuesto in lista_stock:
        cantidad = obtener_numero(repuesto, ["cantidad", "stock", "existencias"])
        valor_unitario = obtener_numero(
            repuesto,
            ["valor_unitario", "precio_unitario", "costo_unitario", "precio"],
        )
        reporte["valor_total_stock"] += cantidad * valor_unitario

    return reporte


def mostrar_reporte_en_pantalla(reporte_dict):
    equipos_por_estado = reporte_dict.get("equipos_por_estado", {})
    preventivos_por_estado = reporte_dict.get("preventivos_por_estado", {})
    correctivos_por_estado = reporte_dict.get("correctivos_por_estado", {})

    print("\n" + "=" * 60)
    print(f"{'REPORTE GENERAL DE MAQUINARIA':^60}")
    print("=" * 60)

    print("\n1. RESUMEN DE EQUIPOS")
    print("-" * 60)
    print(f"{'Total de equipos':<40}{reporte_dict.get('total_equipos', 0):>20}")
    for estado, total in equipos_por_estado.items():
        print(f"{estado:<40}{total:>20}")

    print("\n2. MANTENIMIENTOS PREVENTIVOS")
    print("-" * 60)
    for estado, total in preventivos_por_estado.items():
        print(f"{estado:<40}{total:>20}")
    print(
        f"{'Costo total de preventivos':<40}"
        f"{reporte_dict.get('costo_total_preventivos', 0):>20,.2f}"
    )

    print("\n3. FALLAS CORRECTIVAS")
    print("-" * 60)
    for estado, total in correctivos_por_estado.items():
        print(f"{estado:<40}{total:>20}")
    print(
        f"{'Tickets con prioridad critica':<40}"
        f"{reporte_dict.get('correctivos_prioridad_critica', 0):>20}"
    )

    print("\n4. INVENTARIO DE STOCK")
    print("-" * 60)
    print(f"{'Total de repuestos':<40}{reporte_dict.get('total_repuestos', 0):>20}")
    print(
        f"{'Valor economico total del stock':<40}"
        f"{reporte_dict.get('valor_total_stock', 0):>20,.2f}"
    )

    print("=" * 60 + "\n")


def generar_reporte_critico(lista_correctivos):
    correctivos_criticos = [
        correctivo
        for correctivo in lista_correctivos
        if correctivo.get("estado") == "Pendiente"
        and correctivo.get("prioridad") in ("Cr\u00edtica", "Critica")
    ]

    print("\n" + "!" * 60)
    print(f"{'ALERTA: CORRECTIVOS CRITICOS PENDIENTES':^60}")
    print("!" * 60)

    if not correctivos_criticos:
        print("No hay correctivos criticos pendientes.")
        print("!" * 60 + "\n")
        return

    print(f"{'Codigo':<15}{'Equipo':<25}{'Descripcion':<20}")
    print("-" * 60)

    for correctivo in correctivos_criticos:
        codigo = correctivo.get("codigo", correctivo.get("id", "N/A"))
        equipo = correctivo.get("equipo", correctivo.get("maquinaria", "N/A"))
        descripcion = correctivo.get(
            "descripcion",
            correctivo.get("falla", "Sin descripcion"),
        )
        print(f"{str(codigo):<15}{str(equipo):<25}{str(descripcion):<20}")

    print("!" * 60 + "\n")


def generar_alerta_stock(lista_stock):
    repuestos_bajo_stock = []

    for repuesto in lista_stock:
        cantidad = obtener_numero(repuesto, ["cantidad", "stock", "existencias"])
        stock_minimo = obtener_numero(repuesto, ["stock_minimo", "minimo"])

        if cantidad <= stock_minimo:
            repuestos_bajo_stock.append((repuesto, cantidad, stock_minimo))

    print("\n" + "!" * 60)
    print(f"{'ALERTA: REPUESTOS EN STOCK MINIMO':^60}")
    print("!" * 60)

    if not repuestos_bajo_stock:
        print("No hay repuestos por debajo del stock minimo.")
        print("!" * 60 + "\n")
        return

    print(f"{'Codigo':<15}{'Repuesto':<25}{'Actual':>10}{'Minimo':>10}")
    print("-" * 60)

    for repuesto, cantidad, stock_minimo in repuestos_bajo_stock:
        codigo = repuesto.get("codigo", repuesto.get("id", "N/A"))
        nombre = repuesto.get("nombre", repuesto.get("repuesto", "N/A"))
        print(f"{str(codigo):<15}{str(nombre):<25}{cantidad:>10.0f}{stock_minimo:>10.0f}")

    print("!" * 60 + "\n")


def menu_reportes():
    while True:
        print("\n" + "=" * 60)
        print(f"{'MENU DE REPORTES':^60}")
        print("=" * 60)
        print("1. Ver Reporte General")
        print("2. Ver Alertas de Stock")
        print("3. Ver Correctivos Criticos")
        print("4. Salir")
        print("-" * 60)

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            lista_equipos = cargar_maquinaria()
            lista_preventivos = cargar_mantenimientos()
            lista_correctivos = cargar_correctivos()
            lista_stock = cargar_stock()

            reporte = generar_reporte_general(
                lista_equipos,
                lista_preventivos,
                lista_correctivos,
                lista_stock,
            )
            mostrar_reporte_en_pantalla(reporte)
        elif opcion == "2":
            lista_stock = cargar_stock()
            generar_alerta_stock(lista_stock)
        elif opcion == "3":
            lista_correctivos = cargar_correctivos()
            generar_reporte_critico(lista_correctivos)
        elif opcion == "4":
            print("\nSaliendo del modulo de reportes...\n")
            break
        else:
            print("\nOpcion no valida. Intente nuevamente.")


if __name__ == "__main__":
    menu_reportes()
