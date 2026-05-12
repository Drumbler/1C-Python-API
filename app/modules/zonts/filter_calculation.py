from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.data.dto.zvn_dto import ZPVNParams, ZVNParams
    from app.data.material_collector import MaterialCollector
    from app.utils.custom.ZVNseries_class import ZVNSeries


FILTER_MATERIAL_ABBR = 'н.ст.08'
STANDARD_FILTER_ABBR = 'ст.фильтры'
PREMIUM_FILTER_ABBR = 'премиум.жир'
SPARK_ARRESTER_ABBR = 'искрогас'
NO_FILTER_MARKERS = ('нет', 'без', '-')
FILTER_SIZES = (2, 3, 4, 5, 6)


def vernut_blizaishee(costs: list[float], zont_length: int) -> float:
    while zont_length > 0 and costs[zont_length] == float('inf'):
        zont_length -= 1
    # print(costs[zont_length])
    # print(zont_length)
    return costs[zont_length]


def min_cost_to_fill(zont_length: float, material: float) -> float:
    """
    Рассчитывает минимальную стоимость заполнения жироуловителями.
    Локально округляет ширину до ближайших 100 мм вверх, как в legacy-расчете.
    """
    zont_length_mm = int(round(zont_length * 1000))
    zont_length_steps = (zont_length_mm + 99) // 100

    filter_costs = [
        ((0.059 * 0.57) * 5 + (0.19 * 0.053) * 4 + (0.58 * 0.053) * 4 + (0.06 * 0.08) * 2) * material + 45,
        ((0.059 * 0.57) * 7 + (0.29 * 0.053) * 4 + (0.58 * 0.053) * 4 + (0.06 * 0.08) * 2) * material + 45,
        ((0.059 * 0.57) * 9 + (0.39 * 0.053) * 4 + (0.58 * 0.053) * 4 + (0.06 * 0.08) * 2) * material + 45,
        ((0.059 * 0.57) * 11 + (0.49 * 0.053) * 4 + (0.58 * 0.053) * 4 + (0.06 * 0.08) * 2) * material + 45,
        ((0.059 * 0.57) * 15 + (0.59 * 0.053) * 4 + (0.58 * 0.053) * 4 + (0.06 * 0.08) * 2) * material + 45,
    ]

    costcontainer = [float('inf')] * (zont_length_steps + 1)
    costcontainer[0] = 0
    for length in range(1, zont_length_steps + 1):
        for size, cost in zip(FILTER_SIZES, filter_costs):
            if length >= size:
                costcontainer[length] = min(costcontainer[length], costcontainer[length - size] + cost)
    return vernut_blizaishee(costcontainer, zont_length_steps)


def calculate_filters_cost(
        Series: ZVNSeries,
        MaterialBase: MaterialCollector,
        params: ZVNParams | ZPVNParams) -> float:
    normalized_filter = params.filters.strip().casefold()

    if not normalized_filter:
        return 0
    if normalized_filter.startswith(NO_FILTER_MARKERS):
        return 0

    if normalized_filter == SPARK_ARRESTER_ABBR:
        return ((params.width + 0.49) // 0.5) * MaterialBase.get_price_by_abbr(SPARK_ARRESTER_ABBR)

    if normalized_filter not in (STANDARD_FILTER_ABBR, PREMIUM_FILTER_ABBR):
        print(f'Фильтр/материал {params.filters} не найден в базе данных')
        return 0

    base_filters_cost = min_cost_to_fill(
        params.width,
        MaterialBase.get_price_by_abbr(FILTER_MATERIAL_ABBR),
    )

    if normalized_filter == PREMIUM_FILTER_ABBR:
        base_filters_cost *= 1 + MaterialBase.get_price_by_abbr(PREMIUM_FILTER_ABBR)

    if Series.is_island:
        base_filters_cost *= 2

    return base_filters_cost
