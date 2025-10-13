from typing import Dict
from app.modules.neutral_base import gusset_calc, shelf_calc


# Добавить варианты материалов полок и косынок
def parse_params(parameters: str) -> Dict[str, str]:
    keys = [
        'width',
        'depth',
        'height',
    ]

    values = parameters.split('/')
    return dict(zip(keys, values))


def cost_calculation(series: str, parsed_params: Dict[str, str]) -> float:
    width = float(parsed_params['width'])/1000
    depth = float(parsed_params['depth'])/1000
    height = float(parsed_params['height'])/1000

    gusset_cost = gusset_calc(series, height, depth) * 2
    shelf_cost = shelf_calc(series, width, depth)
    total_cost = (gusset_cost + shelf_cost + 95) * 1.05
    return round(total_cost, 2)


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_params(parameters)
    return cost_calculation(series, parsed_params)
