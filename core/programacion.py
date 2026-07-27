from datetime import datetime, time, timedelta

HORA_INICIO_JORNADA = time(hour=6, minute=0)
HORA_FIN_JORNADA = time(hour=22, minute=0)


def ajustar_inicio_laboral(fecha_hora: datetime) -> datetime:
    """
    Ajusta una fecha y hora al siguiente momento laboral válido.

    Horario laboral:
    - Inicio: 06:00
    - Final: 22:00
    """
    inicio_dia = datetime.combine(
        fecha_hora.date(),
        HORA_INICIO_JORNADA,
    )

    fin_dia = datetime.combine(
        fecha_hora.date(),
        HORA_FIN_JORNADA,
    )

    if fecha_hora < inicio_dia:
        return inicio_dia

    if fecha_hora >= fin_dia:
        return datetime.combine(
            fecha_hora.date() + timedelta(days=1),
            HORA_INICIO_JORNADA,
        )

    return fecha_hora


def sumar_horas_laborales(
    fecha_hora_inicio: datetime,
    horas: float,
) -> datetime:
    """
    Suma horas de producción respetando el horario laboral.

    Cuando se llega a las 22:00, el trabajo continúa
    al día siguiente a las 06:00.
    """
    fecha_hora_actual = ajustar_inicio_laboral(fecha_hora_inicio)

    horas_pendientes = float(horas)

    while horas_pendientes > 0:
        fin_jornada = datetime.combine(
            fecha_hora_actual.date(),
            HORA_FIN_JORNADA,
        )

        horas_disponibles = (fin_jornada - fecha_hora_actual).total_seconds() / 3600

        if horas_pendientes <= horas_disponibles:
            return fecha_hora_actual + timedelta(hours=horas_pendientes)

        horas_pendientes -= horas_disponibles

        fecha_hora_actual = datetime.combine(
            fecha_hora_actual.date() + timedelta(days=1),
            HORA_INICIO_JORNADA,
        )

    return fecha_hora_actual


def crear_programacion(
    ordenes: list[dict],
    inicio_programacion: datetime,
) -> list[dict]:
    """
    Calcula el inicio y final programado de cada OT.

    Por defecto, cada OT comienza al finalizar la anterior.

    Si una OT tiene un inicio manual posterior al momento
    disponible del tren, espera hasta ese inicio manual.
    """
    programacion = []
    hora_disponible = ajustar_inicio_laboral(inicio_programacion)

    for orden in ordenes:
        inicio_orden = hora_disponible

        inicio_manual_texto = orden.get("inicio_manual")

        if inicio_manual_texto:
            try:
                inicio_manual = datetime.fromisoformat(inicio_manual_texto)

                inicio_manual = ajustar_inicio_laboral(inicio_manual)

                inicio_orden = max(inicio_orden, inicio_manual)

            except (TypeError, ValueError):
                # Si el valor guardado no es válido,
                # se ignora y se continúa con la secuencia.
                pass

        inicio_orden = ajustar_inicio_laboral(inicio_orden)

        duracion_programada = float(orden["duracion_horas"])

        # Si una OT fue pausada y luego reanudada,
        # programamos únicamente el tiempo restante.
        horas_producidas = float(orden.get("horas_producidas") or 0)

        if orden["estado"] == "en_produccion":
            duracion_programada = max(
                duracion_programada - horas_producidas,
                0,
            )

        final_orden = sumar_horas_laborales(
            inicio_orden,
            duracion_programada,
        )

        programacion.append(
            {
                **orden,
                "inicio": inicio_orden,
                "final": final_orden,
                "duracion_programada": (duracion_programada),
            }
        )

        hora_disponible = final_orden

    return programacion


def formatear_fecha_hora(valor: datetime) -> str:
    """
    Convierte una fecha y hora al formato utilizado
    en la interfaz.
    """
    return valor.strftime("%d/%m/%Y %H:%M")
