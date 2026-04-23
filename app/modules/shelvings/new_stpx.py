from app.data.dto.shelvings_dto import ProductionShelvingsParams
from app.data.material_collector import MaterialCollector
from app.modules.shelvings_handler import calculate_difficulty_coef, calculate_options_cost, calculate_pillars_cost, calculate_shelfs_cost
from app.utils.custom.shelf_class import ShelfType
from app.utils.custom.shelvings_class import ShelvingSeries


SCHEMA = (
    ProductionShelvingsParams,
    (
        'width',
        'depth',
        'height',
        'ral_pillars',
        'shelf_material',
        'ral_shelfs',
        'shelfs_number',
        'shelfs_order',
        'additional_reinforcement',
        'weld',
        'stands',
    ),
)
SHELF_ORDER_TYPES = {item.value.casefold(): item for item in ShelfType}


def _to_meters(value: str, field_name: str) -> float:
    try:
        return float(value.replace(',', '.')) / 1000
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}: expected number in mm, got {value!r}") from exc


def _to_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}: expected integer, got {value!r}") from exc


def _parse_shelfs_order(value: str) -> list[ShelfType]:
    shelfs_order = []
    for char in value:
        shelf_type = SHELF_ORDER_TYPES.get(char.casefold())
        if shelf_type is None:
            raise ValueError(f"Invalid shelfs_order item: {char!r}")
        shelfs_order.append(shelf_type)
    return shelfs_order


def parse_parameters(parameters: str, series: str) -> ProductionShelvingsParams:
    dto_cls, keys = SCHEMA
    values = [value.strip() for value in parameters.split('/')]

    if len(values) != len(keys):
        raise ValueError(
            f"Expected {len(keys)} parameters for {series}, got {len(values)}"
        )

    data = dict(zip(keys, values))
    data['width'] = _to_meters(data['width'], 'width')
    data['depth'] = _to_meters(data['depth'], 'depth')
    data['height'] = _to_meters(data['height'], 'height')
    data['shelfs_number'] = _to_int(data['shelfs_number'], 'shelfs_number')
    data['shelfs_order'] = _parse_shelfs_order(data['shelfs_order'])

    if len(data['shelfs_order']) != data['shelfs_number']:
        raise ValueError(
            "Shelfs order length must match shelfs number: "
            f"{len(data['shelfs_order'])} != {data['shelfs_number']}"
        )

    return dto_cls(**data)


def cost_calculation(params: ProductionShelvingsParams, series: ShelvingSeries) -> float:
    MatCollector = MaterialCollector(series._value_)
    
    pillars = calculate_pillars_cost(series, MatCollector, params)
    shelfs = calculate_shelfs_cost(MatCollector, params)
    misc = MatCollector.calculate_misc()
    options = calculate_options_cost(MatCollector, params)
    markup = calculate_difficulty_coef(params)

    total_cost = pillars + shelfs + misc + options


    return total_cost * markup, markup


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_parameters(parameters, series)
    FormattedSeries = ShelvingSeries(series)
    total_cost, markup = cost_calculation(parsed_params, FormattedSeries)
    return total_cost, markup
