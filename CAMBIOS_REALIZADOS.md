# Cambios realizados

## Integración

- Se agregó `menu_correctivo()`.
- Se agregó `menu_stock()`.
- Todos los módulos utilizan la carpeta común `datos/`.
- Se agregó `almacenamiento.py` para leer y guardar JSON de forma segura.
- Se eliminó el código de reportes que estaba duplicado dentro de `stock.py`.

## Equipos

- Validación de códigos duplicados.
- Validación de horas negativas, infinitas o `NaN`.
- Normalización de estados.
- Búsqueda y actualización seguras.

## Preventivo

- Estados unificados: Programado, En proceso, Completado y Cancelado.
- Registro de costo estimado o final.
- Validación de fechas.
- Bloqueo de dos preventivos simultáneos para el mismo equipo.
- Sincronización automática del estado de la maquinaria.

## Correctivo

- Corrección del error de `fecha_solucion=None`.
- Generación automática de códigos `MC-0001`.
- Validación de prioridad, estado y fechas.
- Menú completo de registro, búsqueda, listados y cambio de estado.
- Sincronización del estado del equipo con las fallas abiertas.

## Stock

- Se agregaron las importaciones y rutas faltantes.
- Menú completo de inventario.
- Validación de cantidades, precios, categorías y códigos duplicados.
- Entradas y salidas de inventario sin permitir stock negativo.
- Cálculo del valor total y alerta de stock mínimo.

## Reportes

- Corrección de nombres de campos de correctivos y repuestos.
- Detección correcta de correctivos críticos abiertos.
- Conteo de todos los estados reales del sistema.
- Cálculo de costos preventivos y valor del inventario.

## Verificaciones ejecutadas

- Compilación de todos los archivos Python.
- Apertura de los cinco módulos desde el menú principal.
- Flujo completo de equipo, preventivo, correctivo, stock y reportes.
- Validación de códigos duplicados, stock negativo y valores numéricos inválidos.
