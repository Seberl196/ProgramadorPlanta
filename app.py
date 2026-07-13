from datetime import date, datetime, time

import streamlit as st

from database.repository import (
    get_train,
    get_train_configuration,
    update_train_start,
)
from database.schema import initialize_database


TRAIN_ID = 1


def load_initial_data() -> tuple[dict, dict]:
    """
    Inicializa la base de datos y carga la información del Tren 1.
    """
    initialize_database()

    train = get_train(TRAIN_ID)
    configuration = get_train_configuration(TRAIN_ID)

    if train is None:
        raise RuntimeError("No se encontró el Tren 1 en la base de datos.")

    if configuration is None:
        raise RuntimeError(
            "No se encontró la configuración del Tren 1."
        )

    return train, configuration


def parse_stored_datetime(value: str) -> datetime:
    """
    Convierte la fecha almacenada en SQLite a un objeto datetime.
    """
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "La fecha de inicio almacenada no tiene un formato válido."
        ) from error


def combine_date_and_time(
    selected_date: date,
    selected_time: time,
) -> datetime:
    """
    Combina la fecha y la hora seleccionadas por el usuario.
    """
    return datetime.combine(selected_date, selected_time).replace(
        microsecond=0
    )


def main() -> None:
    st.set_page_config(
        page_title="Programación — Tren 1",
        page_icon="🏭",
        layout="wide",
    )

    st.title("Programación — Tren 1")
    st.caption(
        "Primera versión manual del Programador de planta."
    )

    try:
        train, configuration = load_initial_data()
        stored_start = parse_stored_datetime(
            configuration["inicio_programacion"]
        )

    except Exception as error:
        st.error(
            "No fue posible cargar la configuración de la aplicación."
        )
        st.exception(error)
        st.stop()

    st.subheader("Configuración de la programación")

    st.write(
        f"**Línea de producción:** {train['nombre']}"
    )

    with st.form("form_start_configuration"):
        st.markdown("#### Inicio de programación del Tren 1")

        date_column, time_column = st.columns(2)

        with date_column:
            selected_date = st.date_input(
                "Fecha",
                value=stored_start.date(),
                format="DD/MM/YYYY",
            )

        with time_column:
            selected_time = st.time_input(
                "Hora",
                value=stored_start.time(),
                step=60,
            )

        save_button = st.form_submit_button(
            "Guardar inicio de programación",
            type="primary",
        )

    if save_button:
        new_start = combine_date_and_time(
            selected_date,
            selected_time,
        )

        try:
            update_train_start(TRAIN_ID, new_start)

            st.success(
                "El inicio de programación del Tren 1 "
                "se guardó correctamente."
            )

        except Exception as error:
            st.error(
                "No fue posible guardar el inicio de programación."
            )
            st.exception(error)

    st.divider()

    st.info(
        "Todavía no existen órdenes de trabajo. "
        "El registro manual de OT se añadirá en el Bloque 2."
    )


if __name__ == "__main__":
    main()