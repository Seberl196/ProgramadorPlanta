from datetime import datetime
import plotly.graph_objects as go
import streamlit as st

from core.programacion import (
    crear_programacion,
    formatear_fecha_hora,
)
from data.ordenes import (
    obtener_ordenes_pausadas,
    obtener_ordenes_programables,
)
from core.gantt import (
    agrupar_tramos_por_dia,
    calcular_horas_programadas,
    calcular_horas_restantes,
    convertir_hora_a_decimal,
    obtener_titulo_dia,
    obtener_nombre_estado,
)


COLORES_ESTADO = {
    "pendiente": "#7C8DB5",
    "en_produccion": "#58A66A",
    "pausada": "#909090",
}


def _crear_figura_dia(
    fecha,
    tramos: list[dict],
):
    """
    Crea el Gantt fijo correspondiente a un solo día.
    """
    figura = go.Figure()

    etiquetas = []

    for tramo in tramos:
        etiqueta = f"{tramo['posicion']}. {tramo['numero_ot']}"

        etiquetas.append(etiqueta)

        inicio_decimal = convertir_hora_a_decimal(tramo["inicio"])

        final_decimal = convertir_hora_a_decimal(tramo["final"])

        duracion = final_decimal - inicio_decimal

        estado = tramo["estado"]

        figura.add_trace(
            go.Bar(
                x=[duracion],
                y=[etiqueta],
                base=[inicio_decimal],
                orientation="h",
                marker={
                    "color": COLORES_ESTADO.get(
                        estado,
                        "#7C8DB5",
                    ),
                    "line": {
                        "color": "rgba(60, 60, 60, 0.20)",
                        "width": 1,
                    },
                },
                text=[tramo["numero_ot"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont={
                    "size": 13,
                },
                name=obtener_nombre_estado(estado),
                showlegend=False,
                hoverinfo="skip",
                cliponaxis=False,
            )
        )

    etiquetas_unicas = list(dict.fromkeys(etiquetas))

    figura.update_xaxes(
        range=[6, 22],
        tickmode="array",
        tickvals=list(range(6, 23, 2)),
        ticktext=[f"{hora:02d}:00" for hora in range(6, 23, 2)],
        title=None,
        fixedrange=True,
        showgrid=True,
        gridcolor="rgba(150, 150, 150, 0.22)",
        gridwidth=1,
        zeroline=False,
        side="top",
        tickfont={
            "size": 11,
        },
    )

    figura.update_yaxes(
        categoryorder="array",
        categoryarray=etiquetas_unicas,
        autorange="reversed",
        title=None,
        fixedrange=True,
        showgrid=True,
        gridcolor="rgba(160, 160, 160, 0.14)",
        tickfont={
            "size": 12,
        },
    )

    figura.update_layout(
        title={
            "text": (f"<b>{obtener_titulo_dia(fecha)}</b>"),
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 17,
            },
        },
        height=max(
            230,
            145 + len(etiquetas_unicas) * 54,
        ),
        margin={
            "l": 25,
            "r": 20,
            "t": 75,
            "b": 20,
        },
        barmode="overlay",
        bargap=0.28,
        dragmode=False,
        hovermode=False,
        clickmode="none",
        plot_bgcolor="rgba(120, 140, 170, 0.05)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    # Límites visuales de la jornada laboral.
    figura.add_vline(
        x=6,
        line_width=2,
        line_color="rgba(80, 80, 80, 0.42)",
    )

    figura.add_vline(
        x=22,
        line_width=2,
        line_color="rgba(80, 80, 80, 0.42)",
    )

    return figura


def _mostrar_resumen(
    programacion: list[dict],
) -> None:
    """
    Muestra las métricas principales de la programación.
    """
    horas_productivas = calcular_horas_programadas(programacion)

    columna_1, columna_2, columna_3 = st.columns(3)

    with columna_1:
        st.metric(
            "OT en la cola",
            len(programacion),
        )

    with columna_2:
        st.metric(
            "Horas productivas",
            f"{horas_productivas:.2f} h",
        )

    with columna_3:
        st.metric(
            "Final de la programación",
            formatear_fecha_hora(programacion[-1]["final"]),
        )


def _mostrar_pausadas(
        tren_id: int,
) -> None:
    """
    Muestra un resumen de las OT pausadas.
    """
    ordenes_pausadas = obtener_ordenes_pausadas(tren_id=tren_id)

    if not ordenes_pausadas:
        return

    with st.expander(f"OT pausadas ({len(ordenes_pausadas)})"):
        for orden in ordenes_pausadas:
            horas_restantes = calcular_horas_restantes(orden)

            st.write(f"**{orden['numero_ot']}** — {horas_restantes:.2f} h restantes")


def mostrar_gantt_diario(
    inicio_programacion: datetime | None,
    tren_id = int,
) -> None:
    """
    Muestra una vista Gantt separada por jornadas.
    """
    st.subheader("Gantt diario de producción")

    ordenes = obtener_ordenes_programables(tren_id=tren_id)

    if not ordenes:
        st.info("No hay órdenes en la cola activa.")

        _mostrar_pausadas(tren_id=tren_id)
        return

    if inicio_programacion is None:
        st.warning(
            "Debes definir el inicio de la programación antes de mostrar el Gantt."
        )
        return

    programacion = crear_programacion(
        ordenes=ordenes,
        inicio_programacion=inicio_programacion,
    )

    _mostrar_resumen(programacion)

    st.divider()

    tramos_por_dia = agrupar_tramos_por_dia(programacion)

    for fecha, tramos in tramos_por_dia.items():
        figura = _crear_figura_dia(
            fecha=fecha,
            tramos=tramos,
        )

        st.plotly_chart(
            figura,
            use_container_width=True,
            config={
                "staticPlot": True,
                "displayModeBar": False,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": False,
                "showTips": False,
            },
            key=f"gantt_diario_{fecha.isoformat()}",
        )

    st.caption(
        "Cada panel representa una jornada productiva "
        "independiente, desde las 06:00 hasta las 22:00."
    )

    _mostrar_pausadas(tren_id)
