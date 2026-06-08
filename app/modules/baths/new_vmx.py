import re
from dataclasses import dataclass

from app.data.dto.vmx_dto import VMXParams
from app.utils.custom.shelf_class import ShelfType


MATERIAL_FOR_PLATE = 'н.ст.08'
MATERIAL_FOR_BATH = '439.н.ст.10'
MATERIAL_FOR_APRON = 'оц.ст.07'
MATERIAL_FOR_BRACING = 'оц.ст.07'
STANDARD_BATH_COLORS = frozenset((
    'RAL9005',
    'RAL7024',
    'RAL7001',
    'RAL8017',
    'RAL1013',
    'RAL9016',
))
WHEEL_OPTIONS = frozenset(('d100', 'd125', 'd160', 'бампер'))
SHELF_TYPE_ABBRS = frozenset(shelf_type.abbr for shelf_type in ShelfType)


@dataclass(slots=True)
class _BathParseDraft:
    width_bath: float | None
    depth_bath: float | None = None
    height_bath: float | None = None
    type_of_tap_hole: str | None = None
    type_of_drain_hole: str | None = None
    need_onepiece_bath: bool = False
    abbr_onepiece_bath: str | None = None
    welded: bool = False
    wheels: str | None = None
    longer_plate: float = 0.0


def define_abbr_strapping(series_letter: str, welded: bool) -> str:
    if series_letter in {'П', 'Э'} and welded:
        return f'{series_letter}.обв.сварн'
    return f'{series_letter}.обв'


def define_material_reinforce_angle(series_letter: str) -> str:
    reinforce_materials = {
        'Л': 'оц.ст.13',
        'Н': 'н.ст.15',
        'Э': 'н.ст.15',
        'П': 'н.ст.15',
        'Б': 'краш.ст.15',
    }
    return reinforce_materials[series_letter]


def _to_rounded_meters(value: str, field_name: str) -> float:
    try:
        size = int(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid {field_name}: expected integer size in mm, got {value!r}"
        ) from exc
    return ((size + 99) // 100) * 100 / 1000


def _extract_int(value: str, field_name: str) -> int:
    match = re.search(r'(\d+)', value)
    if match is None:
        raise ValueError(f"Invalid {field_name}: expected number in {value!r}")
    return int(match.group(1))


def _extract_series_letter(series: str) -> str:
    normalized_series = series.upper()
    if normalized_series.startswith('ВМ') or normalized_series.startswith('ВК'):
        return normalized_series[2]
    raise ValueError(f"Unsupported bath series: {series}")


def _extract_baths_count(series: str) -> int:
    match = re.search(r'(\d)\s*$', series)
    if match is None:
        raise ValueError(f"Unsupported bath series format: {series}")
    return int(match.group(1))


def _normalize_color(value: str) -> str | None:
    normalized_value = value.strip()
    if normalized_value.casefold() == 'не.краш':
        return None

    upper_value = normalized_value.upper()
    if upper_value in STANDARD_BATH_COLORS:
        return upper_value

    return 'RALzakaz'


def _extract_material_in_parentheses(value: str, field_name: str) -> str:
    match = re.search(r'\(([^)]+)\)', value)
    if match is None:
        raise ValueError(f"Invalid {field_name}: expected material in {value!r}")
    return match.group(1).strip()


def _parse_onepiece_bath(value: str) -> tuple[float, float, float]:
    raw_dimensions = re.sub(r'(?i)^моеч\.отд\.', '', value).strip()
    parts = [part.strip() for part in re.split(r'[xх]', raw_dimensions) if part.strip()]
    if len(parts) != 3:
        raise ValueError(
            "Invalid one-piece bath size: expected WхDхH in "
            f"{value!r}"
        )
    try:
        return tuple(int(part) / 1000 for part in parts)
    except ValueError as exc:
        raise ValueError(f"Invalid one-piece bath size: {value!r}") from exc


def _parse_board_size(value: str, width: float, depth: float) -> float:
    lower_value = value.casefold()
    if 'борт.3ст(' in lower_value:
        return (width + 2 * depth) * (_extract_int(value, 'border size') / 1000)
    if 'борт.2ст.' in lower_value:
        return (width + depth) * (_extract_int(value, 'border size') / 1000)
    if 'борт(' in lower_value:
        return width * (_extract_int(value, 'border size') / 1000)
    if 'объемн.борт' in lower_value:
        return width * 0.04 * 0.09
    return 0


def _parse_shelf(
    value: str,
) -> tuple[str | None, ShelfType | None, bool]:
    lower_value = value.casefold()
    if lower_value == 'полка.нет':
        return None, None, False
    if lower_value.startswith('обвязка.3ст'):
        return None, None, True

    shelf_abbr, separator, _ = lower_value.partition('(')
    if separator and shelf_abbr in SHELF_TYPE_ABBRS:
        return (
            _extract_material_in_parentheses(value, 'shelf'),
            ShelfType.get_type(shelf_abbr),
            False,
        )
    return None, None, False


def _handle_bath_geometry_token(state: _BathParseDraft, value: str) -> None:
    lower_value = value.casefold()
    if 'глуб.м.о' in lower_value:
        state.height_bath = _extract_int(value, 'height_bath') / 1000
        return
    if 'моеч.отд.' in lower_value:
        state.need_onepiece_bath = True
        state.abbr_onepiece_bath = value
        state.width_bath, state.depth_bath, state.height_bath = _parse_onepiece_bath(value)


def _handle_color_token(value: str) -> str | None:
    return _normalize_color(value)


def _handle_border_token(
    value: str,
    width: float,
    depth: float,
) -> float | None:
    if 'борт' not in value.casefold():
        return None
    return _parse_board_size(value, width, depth)


def _handle_tap_count_token(
    value: str,
    *_: object,
) -> int | None:
    if 'смес' not in value.casefold():
        return None
    return _extract_int(value, 'number_of_tap_hole')


def _handle_extended_tap_hole_token(
    state: _BathParseDraft,
    value: str,
    *_: object,
) -> bool:
    if 'отверстие.ув.полка' not in value.casefold():
        return False
    state.type_of_tap_hole = 'отверстие.нст'
    state.longer_plate = 0.05
    return True


def _handle_tap_hole_token(
    state: _BathParseDraft,
    value: str,
    *_: object,
) -> bool:
    lower_value = value.casefold()
    if 'отверстие.ст' not in lower_value and 'отверстие.нст' not in lower_value:
        return False
    state.type_of_tap_hole = lower_value
    return True


def _handle_drain_token(
    state: _BathParseDraft,
    value: str,
    *_: object,
) -> bool:
    lower_value = value.casefold()
    if 'слив.' not in lower_value:
        return False
    state.type_of_drain_hole = lower_value
    return True


def _handle_welded_token(
    state: _BathParseDraft,
    value: str,
    *_: object,
) -> bool:
    if value.casefold() != 'сварн':
        return False
    state.welded = True
    return True


def _handle_wheels_token(
    state: _BathParseDraft,
    value: str,
    *_: object,
) -> bool:
    lower_value = value.casefold()
    if lower_value not in WHEEL_OPTIONS:
        return False
    state.wheels = lower_value
    return True


COMMON_TOKEN_HANDLERS = (
    _handle_extended_tap_hole_token,
    _handle_tap_hole_token,
    _handle_drain_token,
    _handle_welded_token,
    _handle_wheels_token,
)


def _apply_common_token_handlers(
    state: _BathParseDraft,
    value: str,
    width: float,
    depth: float,
) -> bool:
    for handler in COMMON_TOKEN_HANDLERS:
        if handler(state, value, width, depth):
            return True
    return False


def _finalize_bath_sizes(
    state: _BathParseDraft,
    width: float,
    depth: float,
) -> tuple[float, float, float]:
    if state.height_bath is None:
        raise ValueError("Bath depth is required in the 4th parameter")

    width_bath = state.width_bath if state.width_bath is not None else width - 0.1
    depth_bath = (
        state.depth_bath
        if state.depth_bath is not None
        else depth - 0.14 - state.longer_plate
    )
    return width_bath, depth_bath, state.height_bath


def parse_parameters(parameters: str, series: str) -> VMXParams:
    values = [value.strip() for value in parameters.split('/')]
    if len(values) < 4:
        raise ValueError(
            f"Expected at least 4 parameters for {series}, got {len(values)}"
        )

    normalized_series = series.strip().upper()
    width = _to_rounded_meters(values[0], 'width')
    depth = _to_rounded_meters(values[1], 'depth')
    height = _to_rounded_meters(values[2], 'height')
    state = _BathParseDraft(width_bath=0.5 if 'С' in normalized_series else None)
    needed_color = None
    board_size = 0.0
    number_of_tap_hole = 0
    shelf_material = None
    shelf_type = None
    shelf_is_strapping_3sides = False
    position_of_shelf = len(values) - 2

    for index, value in enumerate(values):
        if index == 3:
            _handle_bath_geometry_token(state, value)
            continue
        if index == 4:
            needed_color = _handle_color_token(value)
            continue
        board_size_candidate = _handle_border_token(value, width, depth)
        if board_size_candidate is not None:
            board_size = board_size_candidate
            continue
        tap_count_candidate = _handle_tap_count_token(value)
        if tap_count_candidate is not None:
            number_of_tap_hole = tap_count_candidate
            continue
        if _apply_common_token_handlers(state, value, width, depth):
            continue
        if index == position_of_shelf:
            (
                shelf_material,
                shelf_type,
                shelf_is_strapping_3sides,
            ) = _parse_shelf(value)

    width_bath, depth_bath, height_bath = _finalize_bath_sizes(state, width, depth)

    return VMXParams(
        width=width,
        depth=depth,
        height=height,
        series_letter=_extract_series_letter(normalized_series),
        number_of_baths=_extract_baths_count(normalized_series),
        height_bath=height_bath,
        width_bath=width_bath,
        depth_bath=depth_bath,
        needed_color=needed_color,
        board_size=board_size,
        number_of_tap_hole=number_of_tap_hole,
        type_of_tap_hole=state.type_of_tap_hole,
        type_of_drain_hole=state.type_of_drain_hole,
        need_onepiece_bath=state.need_onepiece_bath,
        abbr_onepiece_bath=state.abbr_onepiece_bath,
        welded=state.welded,
        wheels=state.wheels,
        apron=MATERIAL_FOR_APRON if state.need_onepiece_bath else None,
        shelf_material=shelf_material,
        shelf_type=shelf_type,
        shelf_is_strapping_3sides=shelf_is_strapping_3sides,
    )


def _calculate_drain_components(
    material_db,
    params: VMXParams,
) -> float:
    if not params.type_of_drain_hole:
        return 0.0
    return (
        material_db.get_price_by_abbr(params.type_of_drain_hole)
        * params.number_of_baths
    )


def _calculate_shelf_components(
    material_db,
    params: VMXParams,
    material_strapping: float,
) -> float:
    from app.modules.neutral_base import calculate_default_shelf_cost

    if params.shelf_is_strapping_3sides:
        return -params.width * material_strapping
    if params.shelf_type is None:
        return 0.0
    return calculate_default_shelf_cost(
        material_db,
        params.width,
        params.depth,
        params.shelf_material,
        params.shelf_type,
        None,
    )


def _calculate_onepiece_bath_components(
    material_db,
    params: VMXParams,
) -> float:
    if not params.need_onepiece_bath or not params.abbr_onepiece_bath:
        return 0.0
    return material_db.get_price_by_abbr(params.abbr_onepiece_bath)


def _get_optional_material_cost(
    material_db,
    material_abbr: str | None,
) -> float:
    if not material_abbr:
        return 0.0
    return material_db.get_price_by_abbr(material_abbr)


def cost_calculation(params: VMXParams, series: str) -> tuple[float, float]:
    from app.data.material_collector import MaterialCollector

    material_db = MaterialCollector('ВанныМоечные')
    components = material_db.calculate_misc()
    additional_cost = 0.0
    difficult_of_product = 0.0

    material_plate = material_db.get_price_by_abbr(MATERIAL_FOR_PLATE)
    material_bath = material_db.get_price_by_abbr(MATERIAL_FOR_BATH)
    material_leg = material_db.get_price_by_abbr(f'{params.series_letter}.стойк')
    material_strapping = material_db.get_price_by_abbr(
        define_abbr_strapping(params.series_letter, params.welded)
    )
    material_angle = material_db.get_price_by_abbr(
        define_material_reinforce_angle(params.series_letter)
    )
    material_bracing = material_db.get_price_by_abbr(MATERIAL_FOR_BRACING)
    series_for_lookup = series.strip().upper().replace('К', 'М')
    components += material_db.get_price_by_abbr(f'работа.{series_for_lookup}')
    marginality = 1 + material_db.get_price_by_abbr(f'наценка.{series_for_lookup}')
    components += _calculate_drain_components(material_db, params)
    components += _calculate_shelf_components(
        material_db,
        params,
        material_strapping,
    )
    components += _calculate_onepiece_bath_components(material_db, params)
    tap_hole_cost = _get_optional_material_cost(
        material_db,
        params.type_of_tap_hole,
    )

    need_bracing = 1 if params.number_of_baths != 1 else 0
    bottom_reinforcement = 1 if params.number_of_baths != 1 else 0

    cost_of_strapping = (
        (4 * (params.width - 0.08)) * material_strapping
        + (4 * (params.depth - 0.08)) * material_strapping
    )

    cost_of_plate = (
        (
            (params.width + 0.1) * (params.depth - params.depth_bath + 0.12)
            + (params.depth_bath + 0.14) * (params.width - params.width_bath + 0.12)
        )
        * material_plate
        + params.board_size * material_plate
        + int(params.need_onepiece_bath)
        * (params.number_of_baths - 1)
        * (params.depth_bath + 0.05)
        * 0.03
        * material_plate
    )

    cost_of_sink = (
        (params.height_bath + 0.015)
        * (2 * params.width_bath + 2 * params.depth_bath + 0.04)
        * material_bath
        + params.width_bath * params.depth_bath * material_bath
        + (params.number_of_baths - 1)
        * (params.depth_bath + 0.05)
        * 0.03
        * material_bath
    )

    cost_of_production = (
        cost_of_plate
        + int(not params.need_onepiece_bath) * cost_of_sink
        + cost_of_strapping
        + components
        + need_bracing * 0.24 * 0.21 * material_bracing * 4
        + 4 * (params.height - 0.07) * material_leg
        + bottom_reinforcement * (params.width + 0.1) * 0.25 * material_bath
        + 4 * 0.13 * 0.13 * material_angle
        + params.number_of_tap_hole * tap_hole_cost
    )

    markup = marginality + difficult_of_product + 0.1
    full_cost = cost_of_production * markup + additional_cost
    return full_cost, markup


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_parameters(parameters, series)
    total_cost, _ = cost_calculation(parsed_params, series)
    return round(total_cost, 2)
