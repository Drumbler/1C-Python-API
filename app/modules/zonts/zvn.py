from dataclasses import fields

from app.data.dto.zvn_dto import ZPVNParams, ZVNParams
from app.data.material_collector import MaterialCollector

from app.modules.zvn_handler import calculate_additional_cost, calculate_production_cost, get_marginality, handle_body_calculation
from app.utils.custom.ZVNseries_class import ZVNSeries


ADDITIONAL_PARAM_FIELDS = frozenset((
    'filters',
    'main_cut_out',
    'add_cut_out',
    'lights',
    'fan',
))
SUPPLY_ADDITIONAL_PARAM_FIELDS = frozenset((
    'main_cut_in',
    'add_cut_in',
))
NO_ADDITIONAL_MARKERS = ('нет', 'без', '-')
STANDARD_OPTION_VALUES = frozenset((
    'ст.фильтры',
))
STANDARD_RAL_VALUES = frozenset((
    'не.краш',
    'ral9005',
    'ral7024',
    'ral7001',
    'ral8017',
    'ral1013',
    'ral9016',
))


def is_unusual(Series: ZVNSeries, params: ZVNParams | ZPVNParams) -> bool:
    if params.is_cube:
        return True
    if Series.is_island:
        min_width, max_width, min_depth, max_depth = 0.5, 2.2, 1.2, 2.2
    else:
        min_width, max_width, min_depth, max_depth = 0.5, 2.2, 0.5, 1.4
        if Series.model == '01':
            max_depth = 0.7

    width_is_standard = min_width <= params.width <= max_width
    depth_is_standard = min_depth <= params.depth <= max_depth
    height_is_standard = params.height == 0.4

    return not (width_is_standard and depth_is_standard and height_is_standard)


def has_additional(Series: ZVNSeries, params: ZVNParams | ZPVNParams) -> bool:
    additional_fields = ADDITIONAL_PARAM_FIELDS
    if Series.has_supply:
        additional_fields |= SUPPLY_ADDITIONAL_PARAM_FIELDS

    for field in fields(params):
        if field.name not in additional_fields:
            continue

        value = getattr(params, field.name)
        if not isinstance(value, str):
            continue

        normalized_value = value.strip().casefold()
        if not normalized_value:
            continue
        if normalized_value in STANDARD_OPTION_VALUES:
            continue

        has_no_marker = (
            normalized_value.startswith(NO_ADDITIONAL_MARKERS)
            or normalized_value.endswith(NO_ADDITIONAL_MARKERS)
        )
        if not has_no_marker:
            return True

    ral_value = params.ral.strip().casefold()
    return bool(ral_value and ral_value not in STANDARD_RAL_VALUES)


def vernut_blizaishee(list,zont_length):
    """
    Возвращает ближайшую доступную стоимость для указанной ширины зонта.
    """
    return list[int(zont_length)] if list[int(zont_length)] != float('inf') else vernut_blizaishee(list,zont_length-1)

def min_cost_to_fill(zont_length, material):
    """
    Рассчитывает минимальную стоимость заполнения жироуловителями.
    """
    zont_length *= 10
    fliter_size = [2,3,4,5,6]  # Их размеры 200мм,300мм и т.д.
    JU200 = ((0.059*0.57) * 5 + (0.19*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 45 # Стоимость трудозатрат 45 (было 100) рублей (по хорошему отдельная переменная на вход)
    JU300 = ((0.059*0.57) * 7 + (0.29*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 45
    JU400 = ((0.059*0.57) * 9 + (0.39*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 45
    JU500 = ((0.059*0.57) * 11 + (0.49*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 45
    JU600 = ((0.059*0.57) * 15 + (0.59*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 45
    filter_costs = [JU200,JU300,JU400,JU500,JU600] # Их стоимости

    #costcontainer хранит значения минимальных стоимостей для длин
    costcontainer = [float('inf')] * (int(zont_length) + 1)
    costcontainer[0] = 0  # при длине 0 и стоимость 0
    for length in range(1, int(zont_length) + 1):
        for size, cost in zip(fliter_size, filter_costs):
            if length >= size:
                costcontainer[length] = min(costcontainer[length], costcontainer[length - size] + cost)
    return vernut_blizaishee(costcontainer,zont_length)

def get_difficult_implementation(material_base: MaterialCollector, 
                                 premium: bool, unusual_impementation: bool, 
                                 additional_options: bool, Series: ZVNSeries) -> float:
    markup: float = 0.00
    if Series.is_island:
        markup += material_base.get_price_by_id(357) # островное исполнение @Drumbler
    # markup += material_base.get_price_by_id('') 

    positions = {
        (1, 0, 0): "наценка.премиум",
        (1, 0, 1): "наценка.премиум",
        (1, 1, 0): "наценка.премиум",
        (1, 1, 1): "наценка.премиум",
        (0, 0, 0): "наценка.станд.",
        (0, 0, 1): "наценка.станд.доп.опции",
        (0, 1, 0): "наценка.нестанд.",
        (0, 1, 1): "наценка.нестанд.доп.опции",
    }

    markup += material_base.get_price_by_abbr(positions.get((premium, unusual_impementation, additional_options), "наценка.нестанд.доп.опции"))
    return markup


SCHEMAS = {
    'ЗВН': (
        ZVNParams, [
            'width', 'depth', 'height',
            'body_material', 'backplate_material', 'ral',
            'filters', 'main_cut_out', 'add_cut_out',
            'lights', 'fan', 'weld'
        ]
    ),
    'ЗПВН': (
        ZPVNParams, 
        [
            'width', 'depth', 'height',
            'body_material', 'backplate_material', 'ral',
            'filters', 'main_cut_out', 'add_cut_out',
            'main_cut_in', 'add_cut_in',
            'lights', 'fan', 'weld'
        ]
    )
}


def normalize_series(series: str) -> tuple[str, bool]:
    is_premium = 'ПРЕМИУМ' in series.upper()
    normalized_series = series.replace(' ПРЕМИУМ', '').replace('ПРЕМИУМ', '').strip()
    return normalized_series, is_premium


def parse_parameters(parameters: str, series: str) -> ZVNParams | ZPVNParams:
    normalized_series, is_premium = normalize_series(series)
    raw = [x.strip() for x in parameters.split('/')]
    is_cube = raw[0] == 'CUBE'
    values = raw[1:] if is_cube else raw

    schema = next(
        ((dto_cls, keys) for prefix, (dto_cls, keys) in SCHEMAS.items() if normalized_series.startswith(prefix)),
        None,
    )
    dto_cls, keys = schema

    if len(values) != len(keys):
        raise ValueError(f"Expected {len(keys)} parameters, got {len(values)}")

    data = dict(zip(keys, values))
    data['width'] = float(data['width'])/1000
    data['depth'] = float(data['depth'])/1000
    data['height'] = float(data['height'])/1000
    data['is_cube'] = is_cube
    data['is_premium'] = is_premium

    return dto_cls(**data)


def cost_calculation(params: ZVNParams | ZPVNParams, series: str) -> float:
    FormattedSeries = ZVNSeries(series)
    MatCollector = MaterialCollector(series)

    total_cost = 0

    prices = {
        'body': MatCollector.get_price_by_abbr(params.body_material),
        'backplate': MatCollector.get_price_by_abbr(params.backplate_material),
        'ral': MatCollector.get_price_by_abbr(params.ral),
    }

    body_price = handle_body_calculation(FormattedSeries, MatCollector, params)
    production_cost = calculate_production_cost(FormattedSeries, MatCollector, params)
    additional_cost = calculate_additional_cost(FormattedSeries, MatCollector, params)

    difficulty_coef = get_difficult_implementation(
        MatCollector,
        params.is_premium,
        is_unusual(FormattedSeries, params),
        has_additional(FormattedSeries, params),
        FormattedSeries
    )
    marginality_coef = get_marginality(MatCollector)
    production_coef = 1.10

    total_cost = ((body_price + production_cost) * production_coef) * (1 + marginality_coef + difficulty_coef)
    total_cost += additional_cost
    return total_cost
    


def calculate(parameters: str, series: str) -> float:
    normalized_series, _ = normalize_series(series)
    parsed_params = parse_parameters(parameters, series)
    return cost_calculation(parsed_params, normalized_series)
