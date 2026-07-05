# Sistema de Control de Maquinaria Pesada

Aplicación de consola desarrollada en Python para registrar maquinaria, programar mantenimientos preventivos, reportar fallas correctivas, controlar repuestos y consultar indicadores operativos.

## Requisitos

- Python 3.10 o superior.
- No requiere librerías externas.

## Ejecución

Abra una terminal dentro de la carpeta del proyecto y ejecute:

```bash
python main.py
```

En Windows también puede utilizar:

```bash
py main.py
```

## Estructura del proyecto

```text
COMPU-main/
├── main.py                 Menú principal
├── equipos.py              Registro y actualización de equipos
├── preventivo.py           Mantenimientos preventivos
├── correctivo.py           Fallas y reparaciones correctivas
├── stock.py                Inventario de repuestos
├── reportes.py             Indicadores y alertas
├── almacenamiento.py       Lectura y escritura segura de JSON
└── datos/
    ├── maquinaria.json
    ├── mantenimientos.json
    ├── correctivos.json
    └── stock.json
```

## Módulos

### Equipos

Permite registrar una maquinaria nueva, buscarla por código, actualizar sus horas de uso, modelo, área asignada y estado, y listar el catálogo completo.

Estados permitidos:

- `Operativo`
- `En mantenimiento`
- `Fuera de servicio`

### Mantenimiento preventivo

Permite programar, buscar, iniciar, finalizar y cancelar mantenimientos. Al iniciar un preventivo, el equipo cambia a `En mantenimiento`. Al finalizarlo, el sistema revisa si existe otra tarea abierta antes de devolverlo a `Operativo`.

Estados:

- `Programado`
- `En proceso`
- `Completado`
- `Cancelado`

### Mantenimiento correctivo

Permite registrar fallas, buscar tickets, listar los pendientes y actualizar su estado. Los códigos pueden escribirse manualmente o generarse automáticamente con el formato `MC-0001`.

Prioridades:

- `Baja`
- `Media`
- `Alta`
- `Crítica`

Estados:

- `Reportado`
- `En revisión`
- `En reparación`
- `Resuelto`
- `Cancelado`

Mientras exista un correctivo abierto, el equipo permanece como `Fuera de servicio`.

### Stock

Permite registrar repuestos, buscarlos, listar el inventario, ingresar o retirar cantidades, detectar stock mínimo y calcular el valor económico total.

Para actualizar el stock:

- Número positivo: entrada.
- Número negativo: salida.

### Reportes

Incluye:

- Resumen de equipos por estado.
- Resumen de preventivos y su costo.
- Resumen de correctivos y alertas críticas.
- Repuestos con stock mínimo.
- Valor total del inventario.

## Almacenamiento de datos

Todos los módulos utilizan la misma carpeta `datos`. Los archivos se crean automáticamente cuando no existen. La escritura se realiza mediante un archivo temporal para reducir el riesgo de corrupción del JSON.

No se recomienda editar manualmente los archivos mientras el programa está abierto.
