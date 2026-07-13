# Programador de Planta

Prototipo inicial de un programador de producción para el Tren 1.

## Tecnologías

- Python
- Streamlit
- SQLite

## Estado actual

Bloque 1:

- Entorno de desarrollo preparado.
- Streamlit instalado.
- Base de datos SQLite creada.
- Tabla de órdenes creada automáticamente.
- Página básica de comprobación disponible.

## Ejecutar la aplicación

Activar el entorno virtual:# Programador de Planta

Prototipo de un programador de producción para una planta industrial.

La versión actual gestiona la programación del **Tren 1** mediante una vista Kanban y dos vistas Gantt.

## Versión actual

```text
v0.5.0
Funcionalidades
Crear órdenes de trabajo manualmente.

Definir la duración estimada de cada OT.

Organizar las OT mediante botones para subir y bajar.

Editar:

Número de OT.

Duración.

Inicio programado opcional.

Eliminar OT pendientes con confirmación.

Definir el inicio de una nueva programación.

Calcular automáticamente:

Inicio de cada OT.

Final de cada OT.

Continuación al día siguiente.

Respetar el horario laboral:

06:00 a 22:00.

Fuera de este horario, la producción se pausa.

Iniciar producción.

Pausar producción.

Registrar avance provisional en horas.

Permitir que la siguiente OT comience cuando una OT queda pausada.

Reanudar una OT pausada cuando el tren esté libre.

Registrar la fecha y hora real de finalización.

Utilizar el final real como inicio de la siguiente OT.

Conservar las OT terminadas en SQLite para una futura vista de historial.

Mostrar:

Vista Kanban.

Gantt continuo.

Gantt diario por jornadas.

Tecnologías
Python

Streamlit

SQLite

Plotly

Horario de producción actual
Todos los días
06:00 a 22:00
Por ahora no se consideran:

Fines de semana no laborables.

Festivos.

Descansos.

Mantenimientos.

Calendarios especiales.

Cambios de turno con pausas.

Estructura del proyecto
ProgramadorPlanta/
│
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── pyproject.toml
├── .gitignore
│
├── core/
│   ├── __init__.py
│   ├── gantt.py
│   ├── inicializacion.py
│   └── programacion.py
│
├── data/
│   ├── __init__.py
│   ├── conexion.py
│   ├── estado_tren.py
│   ├── migraciones.py
│   └── ordenes.py
│
└── ui/
    ├── __init__.py
    ├── acciones_ot.py
    ├── dialogos_ot.py
    ├── dialogos_produccion.py
    ├── estilos.py
    ├── formularios.py
    ├── gantt.py
    ├── gantt_diario.py
    ├── mensajes.py
    ├── pagina_tren.py
    └── tarjetas.py
Responsabilidad de los módulos
app.py
Punto de entrada de Streamlit.

Se encarga de:

Configurar la página.

Inicializar la aplicación.

Cargar estilos.

Mostrar mensajes.

Mostrar la pestaña del Tren 1.

core/programacion.py
Contiene la lógica de programación:

Horario laboral.

Ajuste al siguiente momento laboral válido.

Suma de horas laborales.

Cálculo de inicio y final de cada OT.

Inicio programado opcional.

Duración restante de OT reanudadas.

core/gantt.py
Contiene la lógica común de las vistas Gantt:

División de OT en tramos diarios.

Agrupación por fecha.

Cálculo de horas programadas.

Cálculo de horas restantes.

Nombres de días y estados.

core/inicializacion.py
Inicializa y actualiza la estructura de SQLite.

data/conexion.py
Administra la conexión con:

programador_planta.db
data/migraciones.py
Crea y actualiza las tablas sin borrar los datos existentes.

data/ordenes.py
Contiene las operaciones relacionadas con OT:

Crear.

Consultar.

Editar.

Eliminar.

Mover.

Iniciar.

Pausar.

Reanudar.

Terminar.

Consultar pausadas.

Consultar historial.

data/estado_tren.py
Guarda el estado persistente del Tren 1:

Próximo inicio disponible.

Programación activa.

Cierre de la programación.

ui/formularios.py
Contiene:

Formulario para iniciar una programación.

Formulario para añadir una OT.

ui/dialogos_ot.py
Contiene:

Edición de OT.

Confirmación de eliminación.

ui/dialogos_produccion.py
Contiene:

Pausa con registro de avance.

Finalización con fecha y hora real.

ui/acciones_ot.py
Contiene las acciones disponibles según el estado de cada OT.

ui/tarjetas.py
Dibuja las tarjetas de:

OT pendientes.

OT en producción.

OT pausadas.

ui/gantt.py
Muestra el Gantt continuo.

ui/gantt_diario.py
Muestra un Gantt independiente por cada jornada laboral.

Instalación
1. Abrir el proyecto
cd "C:\ruta\al\proyecto\ProgramadorPlanta"
2. Crear el entorno virtual
python -m venv .venv
3. Activar el entorno
.\.venv\Scripts\Activate.ps1
Si PowerShell bloquea la activación:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Después vuelve a activar:

.\.venv\Scripts\Activate.ps1
4. Instalar dependencias
pip install -r requirements.txt
Ejecutar la aplicación
Con el entorno virtual activo:

streamlit run app.py
La aplicación abrirá normalmente en:

http://localhost:8501
Dependencias de desarrollo
Para instalar Ruff y Vulture:

pip install -r requirements-dev.txt
Calidad del código
Ruff
Revisar:

ruff check .
Aplicar correcciones seguras:

ruff check . --fix
Formatear:

ruff format .
Verificar formato:

ruff format --check .
Compilación
python -m compileall -q app.py core data ui
Vulture
vulture app.py core data ui --min-confidence 90
Los resultados de Vulture deben revisarse manualmente antes de eliminar código.

Base de datos
La aplicación crea automáticamente:

programador_planta.db
La base de datos no se incluye en Git.

Tablas actuales:

ordenes
estado_tren
Estados de una OT
pendiente
en_produccion
pausada
terminada
Flujo básico
Pendiente
   ↓
En producción
   ↓
Pausada o terminada
Una OT pausada deja libre el tren para iniciar otra OT.

Una OT pausada puede reanudarse cuando no existe otra OT en producción.

Limitaciones actuales
Esta versión es un prototipo funcional.

Todavía no incluye:

Gestión real de 16 trenes.

Separación de datos por tren.

Maestro de referencias.

Clientes.

Cantidades producidas.

Velocidades de producción.

Eficiencias.

Materiales.

Historial visible.

Usuarios y roles.

Calendarios especiales.

Paradas planificadas.

Indicadores de desempeño.

Integración con ERP.

Próximas versiones
Ideas previstas:

Vista de historial.

Gestión de varios trenes.

Maestro de referencias.

Avance por cantidad producida.

Comparación plan vs. real.

KPI de cumplimiento.

Integración con información de materiales.

Calendarios individuales por tren.

Importación de OT desde otros sistemas.

