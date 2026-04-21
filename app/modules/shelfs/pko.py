from typing import Dict
from app.utils.custom.gusset_class import GussetType
from app.utils.custom.shelf_class import ShelfType
from app.data.material_collector import MaterialCollector
from app.modules.neutral_base import calculate_default_shelf_cost, gusset_calc, shelf_calc


# Добавить варианты материалов полок и косынок
def parse_params(parameters: str) -> Dict[str, str]:
    keys = [
        'width',
        'depth',
        'height',
        'shelf_type',
        'border',
        'gusset_type',
        'mounts',
        'additional_railing',
    ]

    values = parameters.split('/')
    return dict(zip(keys, values))


def cost_calculation(series: str, parsed_params: Dict[str, str]) -> float:
    MatCollector = MaterialCollector(series)

    width = float(parsed_params['width'])/1000
    depth = float(parsed_params['depth'])/1000
    height = float(parsed_params['height'])/1000
    shelf_type = ShelfType.get_type(parsed_params.get('shelf_type'))
    border_size = float(parsed_params.get(
        'border').split('(')[-1].strip(')м'))/1000
    gusset_type = GussetType.get_type(parsed_params.get('gusset_type'))
    mounts = parsed_params.get('mounts')
    additional_railing = parsed_params.get('additional_railing')

    gusset_cost = gusset_calc(MatCollector, height, depth, gusset_type) * 1.05
    shelf_cost = calculate_default_shelf_cost(
        MatCollector, width + border_size, depth + border_size, shelf_type=shelf_type)

    total_cost = (gusset_cost + shelf_cost) * 1.05
    return round(total_cost, 2)


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_params(parameters)
    return cost_calculation(series, parsed_params)
