import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "programador_planta.db"


def obtener_conexion() -> sqlite3.Connection:
    """
    Crea una conexión con SQLite.

    row_factory permite acceder a las columnas
    mediante sus nombres.
    """
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row

    return conexion
