from datetime import datetime

import streamlit as st

from data.historial_movimientos import obtener_movimientos_orden
from data.historial_produccion import obtener_eventos_orden


def mostrar_historial_produccion(
    ordenes: list[dict],
) -> None:
    """
    Muestra las OT y su historial de movimientos y producción.
    """

    st.subheader("Historial de producción")

    if not ordenes:
        st.info("No se encontraron órdenes de trabajo.")
        return

    nombres_estados = {
        "entrada": "Entrada",
        "pendiente": "Pendiente",
        "en_produccion": "En producción",
        "pausada": "Pausada",
        "terminada": "Terminada",
    }

    for orden in ordenes:
        eventos = obtener_eventos_orden(orden["id"])
        movimientos = obtener_movimientos_orden(orden["id"])

        if movimientos:
            recorrido_trenes = []

            for movimiento in movimientos:
                if movimiento["tipo"] in {
                    "asignacion",
                    "movimiento",
                }:
                    recorrido_trenes.append(movimiento["nombre_tren_destino"])

            texto_trenes = " → ".join(dict.fromkeys(recorrido_trenes))
        else:
            texto_trenes = "Sin tren"

        estado = orden["estado"]

        nombre_estado = nombres_estados.get(
            estado,
            estado.capitalize(),
        )

        if estado == "terminada" and orden.get("fecha_fin_real"):
            fecha_fin_formateada = datetime.fromisoformat(
                orden["fecha_fin_real"]
            ).strftime("%d/%m/%Y %H:%M")

            titulo = (
                f"OT {orden['numero_ot']} · "
                f"{texto_trenes} · "
                f"{nombre_estado} {fecha_fin_formateada} · "
                f"{orden['duracion_horas']:.2f} h"
            )

        else:
            titulo = (
                f"OT {orden['numero_ot']} · "
                f"{texto_trenes} · "
                f"{nombre_estado} · "
                f"{orden['duracion_horas']:.2f} h"
            )

        with st.expander(titulo):
            st.write(f"**Duración programada:** {orden['duracion_horas']:.2f} h")

            st.write(f"**Horas producidas:** {orden['horas_producidas']:.2f} h")

            if movimientos:
                st.markdown("#### Asignaciones y movimientos")

                for movimiento in movimientos:
                    fecha_movimiento = datetime.fromisoformat(
                        movimiento["fecha_hora"]
                    ).strftime("%d/%m/%Y %H:%M")

                    if movimiento["tipo"] == "asignacion":
                        st.write(
                            f"**{fecha_movimiento}** · "
                            f"Asignada a "
                            f"{movimiento['nombre_tren_destino']}"
                        )

                    else:
                        st.write(
                            f"**{fecha_movimiento}** · "
                            f"{movimiento['nombre_tren_origen']} → "
                            f"{movimiento['nombre_tren_destino']}"
                        )

            if eventos:
                st.markdown("#### Eventos")

                for evento in eventos:
                    fecha_evento = datetime.fromisoformat(
                        evento["fecha_hora"]
                    ).strftime("%d/%m/%Y %H:%M")

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

            if not movimientos and not eventos:
                st.info(
                    "Esta OT todavía no tiene movimientos "
                    "ni eventos de producción registrados."
                )
