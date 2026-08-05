from datetime import datetime

import streamlit as st

from data.historial_movimientos import obtener_movimientos_orden
from data.historial_produccion import (
    obtener_eventos_orden,
)


def mostrar_historial_produccion(
    ordenes: list[dict],
) -> None:
    """
    Muestra las OT terminadas del tren y su historial de eventos.
    """

    st.subheader("Historial de producción")

    for orden in ordenes:
        fecha_fin = orden.get("fecha_fin_real")

        if fecha_fin:
            fecha_fin_formateada = datetime.fromisoformat(fecha_fin).strftime(
                "%d/%m/%Y %H:%M"
            )
        else:
            fecha_fin_formateada = "Sin fecha"

        eventos = obtener_eventos_orden(orden["id"])
        movimientos = obtener_movimientos_orden(orden["id"])

        if movimientos:
            recorrido_trenes = []

            for movimiento in movimientos:
                if movimiento["tipo"] == "asignacion" or movimiento["tipo"] == "movimiento":
                    recorrido_trenes.append(movimiento["nombre_tren_destino"])

            texto_trenes = " → ".join(dict.fromkeys(recorrido_trenes))
        else:
            texto_trenes = "Sin tren"

        titulo = (
            f"OT {orden['numero_ot']} · "
            f"{texto_trenes} · "
            f"Terminada {fecha_fin_formateada} · "
            f"{orden['duracion_horas']:.2f} h"
        )

        with st.expander(titulo):
            st.write(f"**Duración programada:** {orden['duracion_horas']:.2f} h")

            st.write(f"**Horas producidas:** {orden['horas_producidas']:.2f} h")

            if not eventos:
                st.info("Esta OT no tiene eventos registrados en el historial.")
                continue

            if movimientos:
                st.markdown("#### Asignaciones y movimientos")

                for movimiento in movimientos:
                    fecha_movimiento = datetime.fromisoformat(
                        movimiento["fecha_hora"]
                    ).strftime("%d/%m/%Y %H:%M")

                    if movimiento["tipo"] == "asignacion":
                        st.write(
                            f"**{fecha_movimiento}** · "
                            f"Asignada a {movimiento['nombre_tren_destino']}"
                        )

                    else:
                        st.write(
                            f"**{fecha_movimiento}** · "
                            f"{movimiento['nombre_tren_origen']} → "
                            f"{movimiento['nombre_tren_destino']}"
                        )

            st.markdown("#### Eventos")

            for evento in eventos:
                fecha_evento = datetime.fromisoformat(evento["fecha_hora"]).strftime(
                    "%d/%m/%Y %H:%M"
                )

                nombre_evento = evento["evento"].capitalize()

                if evento["horas_producidas"] is None:
                    st.write(
                        f"**{fecha_evento}** · "
                        f"{evento['nombre_tren']} · "
                        f"{nombre_evento}"
                    )
                else:
                    st.write(
                        f"**{fecha_evento}** · "
                        f"{evento['nombre_tren']} · "
                        f"{nombre_evento} · "
                        f"{evento['horas_producidas']:.2f} h"
                    )
