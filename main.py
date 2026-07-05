"""Punto de entrada del Sistema de Control de Maquinaria Pesada."""

import correctivo
import equipos
import preventivo
import reportes
import stock


def mostrar_encabezado() -> None:
    print("\n" + "=" * 58)
    print(" SISTEMA DE CONTROL DE MAQUINARIA PESADA ".center(58, "="))
    print("=" * 58)
    print("1. Gestión de equipos y catálogo")
    print("2. Mantenimiento preventivo")
    print("3. Mantenimiento correctivo")
    print("4. Control de stock de repuestos")
    print("5. Indicadores y reportes")
    print("6. Salir")
    print("=" * 58)


def main() -> None:
    while True:
        mostrar_encabezado()
        try:
            opcion = input("Seleccione un módulo (1-6): ").strip()
            if opcion == "1":
                equipos.menu_equipos()
            elif opcion == "2":
                preventivo.menu_preventivo()
            elif opcion == "3":
                correctivo.menu_correctivo()
            elif opcion == "4":
                stock.menu_stock()
            elif opcion == "5":
                reportes.menu_reportes()
            elif opcion == "6":
                print("\nCerrando el sistema. Operación finalizada correctamente.")
                break
            else:
                print("\nOpción no válida. Ingrese un número del 1 al 6.")
        except (EOFError, KeyboardInterrupt):
            print("\nSistema cerrado por el usuario.")
            break
        except (ValueError, OSError) as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()
