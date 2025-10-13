
def determine_compressor_power_level(dome_area: float,# Площадь купола, м²
    door_area: float,                                 # Площадь дверей, м²
    pan_area: float,                                  # Площадь ванны (дно), м²
    dome_volume: float,                               # Объём купола, м³
    target_temp_min: int                            # Минимальный температурный режим витрины, °C
) -> int:
    """
    Определяет уровень мощности компрессора (1(300Вт), 2(400Вт), 3(500Вт), 4(600Вт)) на основе
    геометрических параметров витрины и заданного температурного режима.
    """
    AIR_TEMPERATURE = 25
    THERMAL_CONDUCTIVITY_GLASS_8MM = 8
    THERMAL_CONDUCTIVITY_GLASS_4MM = 4
    THERMAL_CONDUCTIVITY_PU_20MM = 0.048
    SPECIFIC_HEAT_HUNID_AIR = 1005.6
    DENSITY_HUMID_AIR = 1.2255
    TARGET_STABILISATION_TIME = 1800
    POWER_RESERVE = 1.2

    temperature_difference = AIR_TEMPERATURE - target_temp_min

    heat_inflows_dome = (
        (
            dome_area * THERMAL_CONDUCTIVITY_GLASS_8MM +
            door_area * THERMAL_CONDUCTIVITY_GLASS_4MM +
            pan_area * THERMAL_CONDUCTIVITY_PU_20MM
        )* (temperature_difference)
    )

    heat_outflow_first_start = (
        (
            dome_volume * DENSITY_HUMID_AIR *
            SPECIFIC_HEAT_HUNID_AIR * temperature_difference
        ) / TARGET_STABILISATION_TIME
    )

    capasity = (heat_inflows_dome + heat_outflow_first_start) * POWER_RESERVE
    match capasity:
        case num if num < 300:
            return 1
        case num if 300 <= num < 400:
            return 2
        case num if 400 <= num < 500:
            return 3
        case num if 500 <= num:
            return 4
    raise RuntimeError('Невозможно определить мощность агрегата')