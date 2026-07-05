"""Indicadores y reportes operativos del sistema de maquinaria."""

from __future__ import annotations

from almacenamiento import cargar_lista


def cargar_json(nombre_archivo: str) -> list[dict]:
    return cargar_lista(nombre_archivo)


def cargar_maquinaria() -> list[dict]:
    return cargar_json("maquinaria.json")


def cargar_mantenimientos() -> list[dict]:
    return cargar_json("mantenimientos.json")


def cargar_correctivos() -> list[dict]:
    return cargar_json("correctivos.json")


def cargar_stock() -> list[dict]:
    return cargar_json("stock.json")


def contar_por_estado(lista_datos: list[dict], estados: tuple[str, ...] | list[str]) -> dict[str, int]:
    conteos = {estado: 0 for estado in estados}
    for dato in lista_datos:
        estado = dato.get("estado")
        if estado in conteos:
            conteos[estado] += 1
    return conteos


def contar_por_campo(lista_datos: list[dict], campo: str) -> dict[str, int]:
    conteos: dict[str, int] = {}
    for dato in lista_datos:
        valor = dato.get(campo)
        if valor not in (None, ""):
            texto = str(valor)
            conteos[texto] = conteos.get(texto, 0) + 1
    return conteos


def obtener_numero(diccionario: dict, claves: list[str] | tuple[str, ...]) -> float:
    for clave in claves:
        valor = diccionario.get(clave)
        try:
            return float(valor)
        except (TypeError, ValueError):
            continue
    return 0.0


def generar_reporte_general(
    lista_equipos: list[dict],
    lista_preventivos: list[dict],
    lista_correctivos: list[dict],
    lista_stock: list[dict],
) -> dict:
    estados_equipos = ("Operativo", "En mantenimiento", "Fuera de servicio")
    estados_preventivos = ("Programado", "En proceso", "Completado", "Cancelado")
    estados_correctivos = ("Reportado", "En revisión", "En reparación", "Resuelto", "Cancelado")

    costo_preventivos = sum(
        obtener_numero(item, ("costo", "costo_total", "valor", "monto"))
        for item in lista_preventivos
    )
    valor_stock = 0.0
    repuestos_bajo_stock = 0
    for repuesto in lista_stock:
        cantidad = obtener_numero(repuesto, ("cantidad", "stock", "existencias"))
        minimo = obtener_numero(repuesto, ("stock_minimo", "minimo"))
        precio = obtener_numero(
            repuesto,
            ("precio_unitario", "valor_unitario", "costo_unitario", "precio"),
        )
        valor_stock += cantidad * precio
        if cantidad <= minimo:
            repuestos_bajo_stock += 1

    correctivos_criticos_abiertos = sum(
        1
        for item in lista_correctivos
        if item.get("prioridad") in {"Crítica", "Critica"}
        and item.get("estado") not in {"Resuelto", "Cancelado"}
    )

    return {
        "total_equipos": len(lista_equipos),
        "equipos_por_estado": contar_por_estado(lista_equipos, estados_equipos),
        "total_preventivos": len(lista_preventivos),
        "preventivos_por_estado": contar_por_estado(lista_preventivos, estados_preventivos),
        "costo_total_preventivos": costo_preventivos,
        "total_correctivos": len(lista_correctivos),
        "correctivos_por_estado": contar_por_estado(lista_correctivos, estados_correctivos),
        "correctivos_prioridad_critica": correctivos_criticos_abiertos,
        "total_repuestos": len(lista_stock),
        "repuestos_bajo_stock": repuestos_bajo_stock,
        "valor_total_stock": valor_stock,
    }


def mostrar_reporte_en_pantalla(reporte: dict) -> None:
    print("\n" + "=" * 64)
    print(f"{'REPORTE GENERAL DE MAQUINARIA':^64}")
    print("=" * 64)

    print("\n1. EQUIPOS")
    print("-" * 64)
    print(f"{'Total de equipos':<44}{reporte.get('total_equipos', 0):>20}")
    for estado, total in reporte.get("equipos_por_estado", {}).items():
        print(f"{estado:<44}{total:>20}")

    print("\n2. MANTENIMIENTOS PREVENTIVOS")
    print("-" * 64)
    print(f"{'Total de preventivos':<44}{reporte.get('total_preventivos', 0):>20}")
    for estado, total in reporte.get("preventivos_por_estado", {}).items():
        print(f"{estado:<44}{total:>20}")
    print(f"{'Costo total':<44}S/ {reporte.get('costo_total_preventivos', 0):>16,.2f}")

    print("\n3. MANTENIMIENTOS CORRECTIVOS")
    print("-" * 64)
    print(f"{'Total de correctivos':<44}{reporte.get('total_correctivos', 0):>20}")
    for estado, total in reporte.get("correctivos_por_estado", {}).items():
        print(f"{estado:<44}{total:>20}")
    print(
        f"{'Correctivos críticos abiertos':<44}"
        f"{reporte.get('correctivos_prioridad_critica', 0):>20}"
    )

    print("\n4. INVENTARIO")
    print("-" * 64)
    print(f"{'Tipos de repuesto':<44}{reporte.get('total_repuestos', 0):>20}")
    print(f"{'Repuestos con stock bajo':<44}{reporte.get('repuestos_bajo_stock', 0):>20}")
    print(f"{'Valor total del stock':<44}S/ {reporte.get('valor_total_stock', 0):>16,.2f}")
    print("=" * 64 + "\n")


def generar_reporte_critico(lista_correctivos: list[dict]) -> list[dict]:
    criticos = [
        item
        for item in lista_correctivos
        if item.get("prioridad") in {"Crítica", "Critica"}
        and item.get("estado") not in {"Resuelto", "Cancelado"}
    ]
    print("\n" + "!" * 72)
    print(f"{'ALERTA: CORRECTIVOS CRÍTICOS ABIERTOS':^72}")
    print("!" * 72)
    if not criticos:
        print("No hay correctivos críticos abiertos.")
        print("!" * 72 + "\n")
        return criticos

    print(f"{'Código':<14}{'Equipo':<14}{'Estado':<18}{'Descripción':<26}")
    print("-" * 72)
    for item in criticos:
        print(
            f"{str(item.get('codigo_correctivo', 'N/A')):<14}"
            f"{str(item.get('codigo_equipo', 'N/A')):<14}"
            f"{str(item.get('estado', 'N/A')):<18}"
            f"{str(item.get('descripcion', 'Sin descripción'))[:25]:<26}"
        )
    print("!" * 72 + "\n")
    return criticos


def generar_alerta_stock(lista_stock: list[dict]) -> list[dict]:
    bajos = []
    for repuesto in lista_stock:
        cantidad = obtener_numero(repuesto, ("cantidad", "stock", "existencias"))
        minimo = obtener_numero(repuesto, ("stock_minimo", "minimo"))
        if cantidad <= minimo:
            bajos.append(repuesto)

    print("\n" + "!" * 64)
    print(f"{'ALERTA: REPUESTOS EN STOCK MÍNIMO':^64}")
    print("!" * 64)
    if not bajos:
        print("No hay repuestos en stock mínimo.")
        print("!" * 64 + "\n")
        return bajos

    print(f"{'Código':<15}{'Repuesto':<25}{'Actual':>12}{'Mínimo':>12}")
    print("-" * 64)
    for repuesto in bajos:
        cantidad = obtener_numero(repuesto, ("cantidad", "stock", "existencias"))
        minimo = obtener_numero(repuesto, ("stock_minimo", "minimo"))
        print(
            f"{str(repuesto.get('codigo_repuesto', 'N/A')):<15}"
            f"{str(repuesto.get('nombre', 'N/A'))[:24]:<25}"
            f"{cantidad:>12.0f}{minimo:>12.0f}"
        )
    print("!" * 64 + "\n")
    return bajos


def menu_reportes() -> None:
    while True:
        print("\n--- MENÚ DE REPORTES ---")
        print("1. Ver reporte general")
        print("2. Ver alertas de stock")
        print("3. Ver correctivos críticos")
        print("4. Volver")
        opcion = input("Seleccione una opción: ").strip()
        try:
            if opcion == "1":
                mostrar_reporte_en_pantalla(
                    generar_reporte_general(
                        cargar_maquinaria(),
                        cargar_mantenimientos(),
                        cargar_correctivos(),
                        cargar_stock(),
                    )
                )
            elif opcion == "2":
                generar_alerta_stock(cargar_stock())
            elif opcion == "3":
                generar_reporte_critico(cargar_correctivos())
            elif opcion == "4":
                break
            else:
                print("Opción no válida.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu_reportes()
