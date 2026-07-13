# Programador de planta

Aplicación web para la programación manual de órdenes de trabajo en líneas de producción.

La primera versión del proyecto se concentra exclusivamente en el Tren 1 y permite definir su fecha y hora inicial de programación.

## Estado actual

Bloque 1 completado:

- Estructura inicial del proyecto.
- Entorno virtual de Python.
- Aplicación básica en Streamlit.
- Base de datos SQLite.
- Creación automática de tablas.
- Registro inicial del Tren 1.
- Configuración individual por tren.
- Persistencia del inicio de programación.

Todavía no se ha implementado:

- Registro de órdenes de trabajo.
- Cálculo de tiempos.
- Secuencia de producción.
- Edición o eliminación de órdenes.
- Estados visuales de materiales.

## Tecnologías

- Python
- Streamlit
- SQLite

## Estructura del proyecto

```text
ProgramadorPlanta/
│
├── app.py
├── crear_bd.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── schema.py
│   └── repository.py
│
├── services/
│   ├── __init__.py
│   ├── calculo_tiempos.py
│   ├── secuencia.py
│   └── validaciones.py
│
├── models/
│   ├── __init__.py
│   └── orden.py
│
├── utils/
│   ├── __init__.py
│   └── formatters.py
│
├── data/
│   └── programador_planta.db
│
├── tests/
└── assets/