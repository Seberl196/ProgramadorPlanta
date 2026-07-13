import streamlit as st

from data.ordenes import (
    iniciar_produccion,
    mover_orden,
    reanudar_produccion,
)
from ui.dialogos_ot import (
    mostrar_dialogo_edicion,
    mostrar_dialogo_eliminacion,
)
from ui.dialogos_produccion import (
    mostrar_dialogo_pausa,
    mostrar_dialogo_terminar,
)
from ui.mensajes import guardar_mensaje


def mostrar_acciones_pendiente(
    orden: dict,
    ultima_posicion: int,
    hay_ot_en_produccion: bool,
) -> None:
    """
    Muestra las acciones disponibles para una OT pendiente.
    """
    columna_subir, columna_bajar = st.columns(2)

    with columna_subir:
        subir_deshabilitado = orden["posicion"] == 1 or (
            hay_ot_en_produccion and orden["posicion"] == 2
        )

        if st.button(
            "⬆️ Subir",
            key=f"subir_{orden['id']}",
            disabled=subir_deshabilitado,
            use_container_width=True,
        ):
            mover_orden(
                orden_id=orden["id"],
                direccion="subir",
            )

            guardar_mensaje(
                f"La OT {orden['numero_ot']} subió de posición.",
                "🔄",
            )

            st.rerun()

    with columna_bajar:
        if st.button(
            "⬇️ Bajar",
            key=f"bajar_{orden['id']}",
            disabled=(orden["posicion"] == ultima_posicion),
            use_container_width=True,
        ):
            mover_orden(
                orden_id=orden["id"],
                direccion="bajar",
            )

            guardar_mensaje(
                f"La OT {orden['numero_ot']} bajó de posición.",
                "🔄",
            )

            st.rerun()

    columna_editar, columna_eliminar = st.columns(2)

    with columna_editar:
        if st.button(
            "✏️ Editar",
            key=f"editar_{orden['id']}",
            use_container_width=True,
        ):
            mostrar_dialogo_edicion(orden)

    with columna_eliminar:
        if st.button(
            "🗑️ Eliminar",
            key=f"eliminar_{orden['id']}",
            use_container_width=True,
        ):
            mostrar_dialogo_eliminacion(orden)

    if orden["posicion"] == 1:
        if st.button(
            "▶️ Iniciar producción",
            key=f"iniciar_{orden['id']}",
            type="primary",
            disabled=hay_ot_en_produccion,
            use_container_width=True,
        ):
            try:
                iniciar_produccion(orden["id"])

                guardar_mensaje(
                    f"La OT {orden['numero_ot']} está en producción.",
                    "▶️",
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))


def mostrar_acciones_en_produccion(
    orden: dict,
) -> None:
    """
    Muestra las acciones de una OT en producción.
    """
    if st.button(
        "⏸️ Pausar producción",
        key=f"pausar_{orden['id']}",
        use_container_width=True,
    ):
        mostrar_dialogo_pausa(orden)

    if st.button(
        "🏁 Terminar producción",
        key=f"terminar_{orden['id']}",
        type="primary",
        use_container_width=True,
    ):
        mostrar_dialogo_terminar(orden)


def mostrar_acciones_pausada(
    orden: dict,
    hay_ot_en_produccion: bool,
) -> None:
    """
    Muestra las acciones de una OT pausada.
    """
    if st.button(
        "▶️ Reanudar producción",
        key=f"reanudar_{orden['id']}",
        type="primary",
        disabled=hay_ot_en_produccion,
        use_container_width=True,
    ):
        try:
            reanudar_produccion(orden["id"])

            guardar_mensaje(
                f"La OT {orden['numero_ot']} fue reanudada.",
                "▶️",
            )

            st.rerun()

        except ValueError as error:
            st.error(str(error))

    if hay_ot_en_produccion:
        st.caption("No se puede reanudar mientras otra OT esté en producción.")

    if st.button(
        "🏁 Terminar producción",
        key=f"terminar_pausada_{orden['id']}",
        use_container_width=True,
    ):
        mostrar_dialogo_terminar(orden)
