from typing import Dict
from app.data.shelf_class import ShelfType
from app.modules.material_collector import MaterialCollector
from app.modules.neutral_base import calculate_default_shelf_cost, calculate_difficulty_сoef, calculate_shelf_reinforcement, pillar_calc
from app.utils.handlers.request_handler import RequestHandler

st_handler = RequestHandler()

'''
Предполагаемый запрос из 1С
стандарт - 3 полки, по факту клиент может выбрать количество полок
диаметр сливной трубы 20мм, 201 AISI нерж.; полки 430 нерж.; материал направляющих 430 нерж.
гастроемкость 2/3 
'''


def parse_params(parameters: str) -> Dict[str, str]:
    keys = [
        'width',
        'depth',
        'height',
        'ral_pillars',
        'shelf_material',
        'ral_shelfs',
        'shelf_count',
        'shelfs_order',
        'reinforcement',
        'isAssembled',
        'stands',
    ]
    values = parameters.split('/')
    if len(values) == len(keys):
        return dict(zip(keys, values))
    else:
        raise ValueError(
            'Too many/not enough parameters. Hint: Check the input parameters in `parse_parameters()` or `calculate()` functions')


def cost_calculation(parsed_params: Dict[str, str], series: str) -> float:
    mat_collector = MaterialCollector(series)
    total_cost = 0

    width = float(parsed_params.get('width', 1200))/1000
    depth = float(parsed_params.get('depth', 600))/1000
    heigth = float(parsed_params.get('height', 1800))/1000

    shelf_count = int(parsed_params.get('ral_pillars'))
    shelf_material = parsed_params.get('shelf_material')
    reinf = parsed_params.get('reinforcement')
    shelfs_order = parsed_params.get('shelfs_order')
    ral_s = parsed_params.get('ral_shelfs')
    
    assembly = parsed_params.get('isAssembled')
    stands = parsed_params.get('stands')

    pillar_cost = pillar_calc(mat_collector, series, width, heigth)

    shelfs_cost: float = 0
    for char in shelfs_order:
        s_type = ShelfType.get_type(char)
        shelfs_cost += calculate_default_shelf_cost(
            mat_collector, width, depth, shelf_material, s_type, ral_s)
        shelfs_cost += calculate_shelf_reinforcement(
            mat_collector, width)
        if reinf == 'усиление.да':
            shelfs_cost += calculate_shelf_reinforcement(
                mat_collector, width)
    misc_cost = mat_collector.calculate_misc()

    tray_cost = calculate_tray_cost(width, depth, mat_collector)
    pipe_cost = calculate_drainage_pipe_cost(mat_collector, heigth)    

    total_cost += mat_collector.get_price_by_abbr(assembly)
    total_cost += mat_collector.get_price_by_abbr(stands)
    total_cost += misc_cost + shelfs_cost + pillar_cost + tray_cost + pipe_cost
    return total_cost * calculate_difficulty_сoef(width, depth, shelf_material)


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_params(parameters)
    return cost_calculation(parsed_params, series)



def calculate_tray_cost(material_base: MaterialCollector, width: float, depth: float) -> float:
    tray_cost = (width + 0.09) * (depth + 0.09) * material_base.get_price_by_id(1)
    return tray_cost


def calculate_drainage_pipe_cost(material_base: MaterialCollector, height: float) -> float:
    # pipe material id 275 or 348
    pipe_length = (height - 0.200)
    pipe_cost = pipe_length * material_base.get_price_by_id(348)
    return pipe_cost
