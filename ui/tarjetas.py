from datetime import datetime

import streamlit as st

from core.gantt import calcular_horas_restantes
from core.programacion import (
    crear_programacion,
    formatear_fecha_hora,
)
from data.ordenes import (
    obtener_ordenes_pausadas,
    obtener_ordenes_programables,
)
from ui.acciones_ot import (
    mostrar_acciones_en_produccion,
    mostrar_acciones_pausada,
    mostrar_acciones_pendiente,
)


def _obtener_clave_tarjeta(orden: dict) -> str:
    """
    Devuelve la clave de estilo correspondiente
    al estado actual de la OT.
    """
    if orden["estado"] == "en_produccion":
        return f"ot_card_produccion_{orden['id']}"

    if orden["estado"] == "pausada":
        return f"ot_card_pausada_{orden['id']}"

    return f"ot_card_pendiente_{orden['id']}"


def _mostrar_datos_orden(orden: dict) -> None:
    """
    Muestra la información principal de una OT.
    """
    titulo = f"### {orden['posicion']}. {orden['numero_ot']}"

    if orden["estado"] == "en_produccion":
        titulo += "  🟢 En producción"

    elif orden["estado"] == "pausada":
        titulo += "  ⏸️ Pausada"

    st.markdown(titulo)

    if orden["estado"] == "en_produccion":
        st.caption("Producción activa")

    elif orden["estado"] == "pausada":
        st.caption("Producción detenida temporalmente")

    st.write(f"**Duración:** {orden['duracion_horas']:.2f} horas")

    if orden.get("inicio_manual"):
        try:
            inicio_manual = datetime.fromisoformat(orden["inicio_manual"])

            st.write(
                f"**Inicio programado mínimo:** {formatear_fecha_hora(inicio_manual)}"
            )

        except (TypeError, ValueError):
            pass

    if orden["estado"] == "pausada":
        horas_producidas = float(orden.get("horas_producidas") or 0)

        horas_restantes = max(
            float(orden["duracion_horas"]) - horas_producidas,
            0,
        )

        st.write(f"**Horas producidas:** {horas_producidas:.2f}")

        st.write(f"**Horas restantes:** {horas_restantes:.2f}")

    st.write(f"**Inicio:** {formatear_fecha_hora(orden['inicio'])}")

    st.write(f"**Final:** {formatear_fecha_hora(orden['final'])}")

    if orden["inicio"].date() != orden["final"].date():
        st.caption("Esta OT continúa al día siguiente.")


def mostrar_tarjeta_orden(
    orden: dict,
    ultima_posicion: int,
    hay_ot_en_produccion: bool,
    tren_id: int,
) -> None:
    """
    Muestra una tarjeta de la cola activa.
    """
    clave_tarjeta = _obtener_clave_tarjeta(orden)

    with st.container(
        border=True,
        key=clave_tarjeta,
    ):
        datos, acciones = st.columns([4, 2])

        with datos:
            _mostrar_datos_orden(orden)

        with acciones:
            if orden["estado"] == "pendiente":
                mostrar_acciones_pendiente(
                    orden=orden,
                    ultima_posicion=ultima_posicion,
                    hay_ot_en_produccion=hay_ot_en_produccion,
                    tren_id=tren_id,
                )

            elif orden["estado"] == "en_produccion":
                mostrar_acciones_en_produccion(
                    orden=orden,
                    tren_id=tren_id,
                )


def _mostrar_tarjeta_pausada(
    orden: dict,
    hay_ot_en_produccion: bool,
    tren_id: int,
) -> None:
    """
    Muestra una OT pausada fuera de la cola activa.
    """
    duracion_total = float(orden["duracion_horas"])
    horas_producidas = float(orden.get("horas_producidas") or 0)
    horas_restantes = calcular_horas_restantes(orden)

    clave_tarjeta = f"ot_card_pausada_{orden['id']}"

    with st.container(
        border=True,
        key=clave_tarjeta,
    ):
        datos, acciones = st.columns([4, 2])

        with datos:
            st.markdown(f"### {orden['numero_ot']}  ⏸️ Pausada")
            st.caption("Esta OT está fuera de la cola activa.")
            st.write(f"**Duración total:** {duracion_total:.2f} horas")
            st.write(f"**Horas producidas:** {horas_producidas:.2f} horas")
            st.write(f"**Horas restantes:** {horas_restantes:.2f} horas")

        with acciones:
            mostrar_acciones_pausada(
                orden=orden,
                hay_ot_en_produccion=hay_ot_en_produccion,
                tren_id=tren_id,
            )


def mostrar_programacion(
    inicio_programacion,
    tren_id: int,
) -> None:
    """
    Muestra por separado:

    - OT pausadas.
    - Cola activa del tren seleccionado.
    """
    ordenes_programables = obtener_ordenes_programables(
        tren_id=tren_id,
    )

    ordenes_pausadas = obtener_ordenes_pausadas(
        tren_id=tren_id,
    )

    hay_ot_en_produccion = any(
        orden["estado"] == "en_produccion"
        for orden in ordenes_programables
    )

    if ordenes_pausadas:
        st.subheader("OT pausadas")

        for orden in ordenes_pausadas:
            _mostrar_tarjeta_pausada(
                orden=orden,
                hay_ot_en_produccion=hay_ot_en_produccion,
                tren_id=tren_id,
            )

        st.divider()

    st.subheader("Órdenes programadas")

    if not ordenes_programables:
        st.info("No hay órdenes en la cola activa.")
        return

    if inicio_programacion is None:
        st.warning(
            "Debes definir el inicio de la programación "
            "antes de calcular los horarios."
        )
        return

    programacion = crear_programacion(
        ordenes=ordenes_programables,
        inicio_programacion=inicio_programacion,
    )

    ultima_posicion = len(programacion)

    for orden in programacion:
        mostrar_tarjeta_orden(
            orden=orden,
            ultima_posicion=ultima_posicion,
            hay_ot_en_produccion=hay_ot_en_produccion,
            tren_id=tren_id,
        )
