import sqlite3
import sys

from database.connection import DATABASE_PATH
from database.schema import initialize_database


def main() -> None:
    """
    Crea e inicializa la base de datos del Programador de planta.
    """
    try:
        initialize_database()

        print("Base de datos creada e inicializada correctamente.")
        print(f"Ubicación: {DATABASE_PATH}")

    except sqlite3.Error as error:
        print("No fue posible crear la base de datos.")
        print(f"Detalle técnico: {error}")
        sys.exit(1)

    except Exception as error:
        print("Ocurrió un error inesperado.")
        print(f"Detalle técnico: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()