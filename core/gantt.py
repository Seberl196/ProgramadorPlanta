from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from core.programacion import (
    HORA_FIN_JORNADA,
    HORA_INICIO_JORNADA,
)


NOMBRES_ESTADO = {
    "pendiente": "Pendiente",
    "en_produccion": "En producción",
    "pausada": "Pausada",
    "terminada": "Terminada",
}


DIAS_SEMANA = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]


def obtener_nombre_estado(estado: str) -> str:
    """
    Devuelve el nombre visible de un estado.
    """
    return NOMBRES_ESTADO.get(
        estado,
        estado,
    )


def dividir_orden_en_tramos(
    orden: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Divide una OT en tramos productivos diarios.

    Una OT que cruza las 22:00 continúa al día
    siguiente a las 06:00.
    """
    tramos = []

    inicio_actual = orden["inicio"]
    final_orden = orden["final"]
    numero_tramo = 1

    while inicio_actual < final_orden:
        fin_jornada = datetime.combine(
            inicio_actual.date(),
            HORA_FIN_JORNADA,
        )

        final_tramo = min(
            final_orden,
            fin_jornada,
        )

        tramos.append(
            {
                "fecha": inicio_actual.date(),
                "numero_ot": orden["numero_ot"],
                "posicion": orden["posicion"],
                "estado": orden["estado"],
                "inicio": inicio_actual,
                "final": final_tramo,
                "tramo": numero_tramo,
            }
        )

        if final_tramo >= final_orden:
            break

        inicio_actual = datetime.combine(
            inicio_actual.date() + timedelta(days=1),
            HORA_INICIO_JORNADA,
        )

        numero_tramo += 1

    return tramos


def dividir_programacion_en_tramos(
    programacion: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Divide todas las OT de una programación
    en tramos productivos diarios.
    """
    tramos = []

    for orden in programacion:
        tramos.extend(dividir_orden_en_tramos(orden))

    return tramos


def agrupar_tramos_por_dia(
    programacion: list[dict[str, Any]],
) -> dict:
    """
    Agrupa los tramos de producción por fecha.
    """
    tramos_por_dia = defaultdict(list)

    for tramo in dividir_programacion_en_tramos(programacion):
        tramos_por_dia[tramo["fecha"]].append(tramo)

    return dict(
        sorted(
            tramos_por_dia.items(),
            key=lambda elemento: elemento[0],
        )
    )


def convertir_hora_a_decimal(
    fecha_hora: datetime,
) -> float:
    """
    Convierte una hora a formato decimal.

    Ejemplo:
    08:30 -> 8.5
    """
    return fecha_hora.hour + fecha_hora.minute / 60 + fecha_hora.second / 3600


def obtener_titulo_dia(fecha) -> str:
    """
    Devuelve el nombre completo y la fecha de un día.
    """
    nombre_dia = DIAS_SEMANA[fecha.weekday()]

    return f"{nombre_dia} {fecha.strftime('%d/%m/%Y')}"


def obtener_nombre_dia_corto(
    fecha: datetime,
) -> str:
    """
    Devuelve el nombre corto del día.
    """
    nombres_cortos = [
        "Lun",
        "Mar",
        "Mié",
        "Jue",
        "Vie",
        "Sáb",
        "Dom",
    ]

    return nombres_cortos[fecha.weekday()]


def calcular_horas_programadas(
    programacion: list[dict[str, Any]],
) -> float:
    """
    Suma las horas productivas de la programación.
    """
    return sum(
        float(
            orden.get(
                "duracion_programada",
                orden["duracion_horas"],
            )
        )
        for orden in programacion
    )


def calcular_horas_restantes(
    orden: dict[str, Any],
) -> float:
    """
    Calcula las horas restantes de una OT pausada.
    """
    duracion_total = float(orden["duracion_horas"])

    horas_producidas = float(orden.get("horas_producidas") or 0)

    return max(
        duracion_total - horas_producidas,
        0,
    )
