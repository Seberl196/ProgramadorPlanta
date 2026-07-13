from data.migraciones import (
    inicializar_base_de_datos,
)


def inicializar_aplicacion() -> None:
    """
    Inicializa y actualiza la base de datos.
    """
    inicializar_base_de_datos()
