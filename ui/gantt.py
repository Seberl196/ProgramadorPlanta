from datetime import datetime, timedelta

import plotly.express as px
import streamlit as st

from core.programacion import (
    HORA_FIN_JORNADA,
    HORA_INICIO_JORNADA,
    crear_programacion,
    formatear_fecha_hora,
)
from data.ordenes import (
    obtener_ordenes_pausadas,
    obtener_ordenes_programables,
)
from core.gantt import (
    calcular_horas_programadas,
    calcular_horas_restantes,
    dividir_programacion_en_tramos,
    obtener_nombre_dia_corto,
    obtener_nombre_estado,
)


def _obtener_rango_visual(
    programacion: list[dict],
) -> tuple[datetime, datetime]:
    """
    Obtiene el rango completo que se mostrará en el Gantt.

    La vista comienza a las 06:00 del primer día
    y termina a las 22:00 del último día.
    """
    primer_dia = min(orden["inicio"] for orden in programacion).date()

    ultimo_dia = max(orden["final"] for orden in programacion).date()

    inicio_visual = datetime.combine(
        primer_dia,
        HORA_INICIO_JORNADA,
    )

    final_visual = datetime.combine(
        ultimo_dia,
        HORA_FIN_JORNADA,
    )

    return inicio_visual, final_visual


def _obtener_dias_del_rango(
    inicio_visual: datetime,
    final_visual: datetime,
) -> list[datetime]:
    """
    Devuelve todos los días incluidos en la vista.
    """
    dias = []
    dia_actual = inicio_visual

    while dia_actual.date() <= final_visual.date():
        dias.append(dia_actual)

        dia_actual += timedelta(days=1)

    return dias


def _crear_datos_gantt(
    programacion: list[dict],
) -> list[dict]:
    """
    Adapta los tramos al formato del Gantt continuo.
    """
    datos = []

    for tramo in dividir_programacion_en_tramos(programacion):
        datos.append(
            {
                "OT": tramo["numero_ot"],
                "Etiqueta": (f"{tramo['posicion']}. {tramo['numero_ot']}"),
                "Inicio": tramo["inicio"],
                "Final": tramo["final"],
                "Estado": obtener_nombre_estado(tramo["estado"]),
            }
        )

    return datos


def _añadir_separacion_dias(
    figura,
    inicio_visual: datetime,
    final_visual: datetime,
) -> None:
    """
    Dibuja:

    - Fondo gris para el tiempo NO productivo (22:00-06:00).
    - Fondo blanco para el tiempo productivo.
    - Separador entre días.
    - Encabezado de cada día.
    """

    dias = _obtener_dias_del_rango(
        inicio_visual,
        final_visual,
    )

    for dia in dias:
        inicio_jornada = datetime.combine(
            dia.date(),
            HORA_INICIO_JORNADA,
        )

        fin_jornada = datetime.combine(
            dia.date(),
            HORA_FIN_JORNADA,
        )

        inicio_noche = fin_jornada

        fin_noche = datetime.combine(
            dia.date() + timedelta(days=1),
            HORA_INICIO_JORNADA,
        )

        # ==========================
        # Tiempo NO PRODUCTIVO
        # ==========================

        figura.add_vrect(
            x0=inicio_noche,
            x1=fin_noche,
            fillcolor="rgba(170,170,170,0.28)",
            line_width=0,
            layer="below",
        )

        # ==========================
        # Inicio del día
        # ==========================

        figura.add_vline(
            x=inicio_jornada,
            line_width=1.5,
            line_color="rgba(90,90,90,0.45)",
            layer="below",
        )

        # ==========================
        # Fin del día laboral
        # ==========================

        figura.add_vline(
            x=fin_jornada,
            line_width=1,
            line_color="rgba(120,120,120,0.30)",
            layer="below",
            line_dash="dot",
        )

        # ==========================
        # Nombre del día
        # ==========================

        punto_medio = inicio_jornada + (fin_jornada - inicio_jornada) / 2

        figura.add_annotation(
            x=punto_medio,
            y=1.08,
            xref="x",
            yref="paper",
            text=f"<b>{obtener_nombre_dia_corto(dia)} {dia.strftime('%d/%m')}</b>",
            showarrow=False,
            font=dict(size=15),
        )


def _mostrar_resumen(
    programacion: list[dict],
) -> None:
    """
    Muestra métricas sencillas sobre la programación.
    """
    horas_programadas = calcular_horas_programadas(programacion)

    resumen_1, resumen_2, resumen_3 = st.columns(3)

    with resumen_1:
        st.metric(
            "OT en la cola",
            len(programacion),
        )

    with resumen_2:
        st.metric(
            "Horas productivas",
            f"{horas_programadas:.2f} h",
        )

    with resumen_3:
        st.metric(
            "Final de la programación",
            formatear_fecha_hora(programacion[-1]["final"]),
        )


def _mostrar_ot_pausadas(
        tren_id: int,
) -> None:
    """
    Muestra un resumen de las OT pausadas.

    No aparecen como barras porque actualmente no ocupan
    el Tren 1 ni forman parte de la cola activa.
    """
    ordenes_pausadas = obtener_ordenes_pausadas(tren_id=tren_id)

    if not ordenes_pausadas:
        return

    with st.expander(f"OT pausadas ({len(ordenes_pausadas)})"):
        for orden in ordenes_pausadas:
            horas_restantes = calcular_horas_restantes(orden)

            st.write(f"**{orden['numero_ot']}** — {horas_restantes:.2f} h restantes")


def mostrar_gantt(
    inicio_programacion: datetime | None,
    tren_id : int,
) -> None:
    """
    Muestra el Gantt de la cola activa del tren.
    """
    st.subheader("Gantt de producción")

    ordenes = obtener_ordenes_programables(tren_id)

    if not ordenes:
        st.info("No hay órdenes en la cola activa.")

        _mostrar_ot_pausadas(tren_id=tren_id)
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

    datos_gantt = _crear_datos_gantt(programacion)

    inicio_visual, final_visual = _obtener_rango_visual(programacion)

    figura = px.timeline(
        datos_gantt,
        x_start="Inicio",
        x_end="Final",
        y="Etiqueta",
        color="Estado",
        text="OT",
        category_orders={
            "Etiqueta": [
                (f"{orden['posicion']}. {orden['numero_ot']}") for orden in programacion
            ],
        },
        color_discrete_map={
            "Pendiente": "#7C8DB5",
            "En producción": "#58A66A",
            "Pausada": "#909090",
        },
    )

    _añadir_separacion_dias(
        figura=figura,
        inicio_visual=inicio_visual,
        final_visual=final_visual,
    )

    figura.update_yaxes(
        autorange="reversed",
        title=None,
        showgrid=False,
        tickfont={
            "size": 13,
        },
    )

    figura.update_xaxes(
        range=[
            inicio_visual,
            final_visual,
        ],
        title=None,
        tickformat="%H:%M",
        dtick=2 * 60 * 60 * 1000,
        showgrid=True,
        gridcolor="rgba(180, 180, 180, 0.22)",
        gridwidth=1,
        tickfont={
            "size": 11,
        },
        fixedrange=True,
    )

    figura.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        textfont={
            "size": 12,
        },
        hoverinfo="skip",
        hovertemplate=None,
        cliponaxis=False,
    )

    figura.update_layout(
        height=max(
            380,
            150 + len(programacion) * 70,
        ),
        margin={
            "l": 20,
            "r": 20,
            "t": 80,
            "b": 30,
        },
        legend_title_text="Estado",
        bargap=0.28,
        dragmode=False,
        hovermode=False,
        clickmode="none",
        plot_bgcolor="rgba(0, 0, 0, 0)",
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
    )

    st.caption(
        "Las franjas grises representan tiempo no productivo "
        "(22:00-06:00). "
        "Las barras solo se dibujan durante horas laborales."
    )

    st.caption(
        "Las horas entre las 22:00 y las 06:00 no se muestran como tiempo productivo."
    )

    _mostrar_ot_pausadas(tren_id)
