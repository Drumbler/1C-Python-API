def calculate_individual_cost_of_production(
    series: str,
    width: float,
    height: float,
    material: float,
) -> float:
    """
    Логика расчета individual_cost_of_production, вынесенная из zonts.py.
    """
    individual_cost_of_production = 0

    if series == "ЗПВН-01" or series == "ЗВН-01" or \
        series == "ЗПВН-04/01" or series == "ЗВН-04/01" or \
        series == "ЗПВН-02" or series == "ЗВН-02" or \
        series == "ЗПВН-04/02" or series == "ЗВН-04/02":
        if '01' in series:
            if 'П' in series:
                individual_cost_of_production = (
                    (width - 0.005) * 0.20 * material # Полка
                )
            else:
                individual_cost_of_production = 0
        else:
            if 'П' in series:
                individual_cost_of_production = (
                    # Полка
                    (width - 0.005) * 0.17 * material +
                    # Приток
                    (width - 0.005) * (height + 0.3) * material
                )
            else:
                individual_cost_of_production = width * 0.17 * material  # Полка
    elif series == "ЗПВН-03" or series == "ЗВН-03" or \
        series == "ЗПВН-04/03" or series == "ЗВН-04/03" or \
        series == "ЗПВН-05" or series == "ЗВН-05" or \
        series == "ЗПВН-04/05" or series == "ЗВН-04/05":
        if 'П' in series:
            individual_cost_of_production = (
                # Полка
                (width - 0.005) * 0.17 * material +
                # Приток
                (width - 0.005) * (height + 0.3) * material
            )
        else:
            individual_cost_of_production = width * 0.17 * material # Полка

    return individual_cost_of_production
