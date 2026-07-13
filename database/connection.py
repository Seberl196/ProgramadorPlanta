from pathlib import Path
import sqlite3


# Carpeta raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Carpeta y archivo donde se almacenará la base de datos.
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "programador_planta.db"


def get_connection() -> sqlite3.Connection:
    """
    Crea y devuelve una conexión a la base de datos SQLite.

    La función garantiza que la carpeta 'data' exista antes de
    intentar abrir la base de datos.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    # Permite acceder a las columnas por nombre:
    # fila["nombre"] en lugar de fila[0].
    connection.row_factory = sqlite3.Row

    # Activa el control de claves foráneas en SQLite.
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection