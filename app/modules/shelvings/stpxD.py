from typing import Dict


from app.data.material_collector import MaterialCollector
from app.modules.neutral_base import calculate_default_shelf_cost, calculate_difficulty_сoef, calculate_plank_racks_and_backwalls, calculate_shelf_reinforcement, pillar_calc
def parse_params(parameters: str) -> dict:
    keys = [
        'width',
        'depth',
        'height',
        'ral_pillars',
        'shelf_count',
        'additional_reinf',
        'is_assembled'
    ]

    values = parameters.split('/')
    if len(keys) == len(values):
        return dict(zip(keys, values))
    else:
        raise ValueError(
            'Too many/not enough parameters. Hint: Check the input parameters in `parse_parameters()` or `calculate()` functions'
            )


def cost_calculation(parsed_params: Dict[str, str], series: str) -> float:
    mat_collector = MaterialCollector(series)
    total_cost = 0

    width = float(parsed_params.get('width', 0))/1000
    depth = float(parsed_params.get('depth', 0))/1000
    height = float(parsed_params.get('height', 0))/1000

    shelf_count = int(parsed_params.get('shelf_count'))
    additional_reinf = parsed_params.get('additional_reinf')

    ral_p = parsed_params.get('ral_pillars')
    assembly = parsed_params.get('is_assembled')

    pillar_cost = pillar_calc(mat_collector, series, width, height, ral_p)

    shelf_cost = calculate_default_shelf_cost(mat_collector, width, depth)
    
    shelf_cost += calculate_shelf_reinforcement(mat_collector, width) * (2 if additional_reinf == 'усиление.да' else 1)
    shelf_cost += calculate_plank_racks_and_backwalls(mat_collector, width, depth)
    shelf_cost = shelf_cost * shelf_count

    misc_cost = mat_collector.calculate_misc()
    total_cost += mat_collector.get_price_by_abbr(assembly)
    total_cost += pillar_cost + misc_cost + shelf_cost
    return total_cost * calculate_difficulty_сoef(width, depth, mat_collector.materials.get(1)[1])


def calculate(series: str, parameters: str) -> float:
    parsed_params = parse_params(parameters)
    total_cost = cost_calculation(series, parsed_params)
    return round(total_cost, 2)