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
PREFERRED_FILTER_SIZES = (3, 4, 5)
FILTER_WORK_COST = 45
FILTER_LAMELLA_COUNTS = {
    2: 5,
    3: 7,
    4: 9,
    5: 11,
    6: 15,
}

def get_filter_unit_cost(filter_size: int, material: float) -> float:
    first_angle_length = (filter_size / 10) - 0.01
    return (
        ((0.059 * 0.57) * FILTER_LAMELLA_COUNTS[filter_size]) +
        ((first_angle_length * 0.053) * 4) +
        ((0.58 * 0.053) * 4) +
        ((0.06 * 0.08) * 2)
    ) * material + FILTER_WORK_COST


def get_filter_layout_rank(layout: tuple[int, ...]) -> tuple[int, int, tuple[int, ...]]:
    if not layout:
        return 0, 0, ()
    return len(layout), max(layout) - min(layout), tuple(-size for size in reversed(layout))


def select_filter_layout(zont_length_steps: int) -> tuple[int, ...]:
    layouts: list[tuple[int, ...] | None] = [None] * (zont_length_steps + 1)
    layouts[0] = ()

    for length in range(1, zont_length_steps + 1):
        best_layout: tuple[int, ...] | None = None
        for size in PREFERRED_FILTER_SIZES:
            if length < size:
                continue

            previous_layout = layouts[length - size]
            if previous_layout is None:
                continue

            candidate_layout = tuple(sorted(previous_layout + (size,)))
            # При равном количестве деталей предпочитаем более ровную раскладку, как в Excel.
            if (
                best_layout is None or
                get_filter_layout_rank(candidate_layout) < get_filter_layout_rank(best_layout)
            ):
                best_layout = candidate_layout

        layouts[length] = best_layout

    selected_layout = layouts[zont_length_steps]
    if selected_layout is None:
        raise ValueError(f'No filter layout found for length step {zont_length_steps}')
    return selected_layout


def get_filter_layout_cost(layout: tuple[int, ...], material: float) -> float:
    return sum(get_filter_unit_cost(filter_size, material) for filter_size in layout)


def min_cost_to_fill(zont_length: float, material: float) -> float:
    """
    Сохраняем legacy-имя функции, но раскладку подбираем по шаблонам из Excel.
    """
    zont_length_mm = int(round(zont_length * 1000))
    zont_length_steps = (zont_length_mm + 99) // 100
    selected_layout = select_filter_layout(zont_length_steps)
    return get_filter_layout_cost(selected_layout, material)


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
