from app.data.classes import ShelfType
from app.modules.material_collector import MaterialCollector
from typing import Dict
from app.modules.neutral_base import border_calc, cabinet_calc, calculate_default_shelf_cost, calculate_table_shelf_cost, parse_type_material, pillar_calc, crossmember_calc, tabletop_calc
from app.utils.custom_funcs import split_to_float


'''
Модуль расчета разборных столов
Пример запроса в модуль:
/Ширина/Глубина/Материал полки/Материал столешницы
'''


def parse_params(parameters: str) -> Dict[str, str]:
    keys = [
        '0',
        'width',
        'depth',
        'height',
        'color',

        'shelf_type_material',
        'shelf_count',
        'tabletop_material',
        'tabletop_underlayment',
        'tabletop_rounding',
        'border',
        'border_fold',  # да, нет
        'cabinet_count',
        'cabinet_size',  # Ширина х Глубина
        'pillars',  # перф/стандарт
        'pillar_wheels',
        'back_pillars_indent',
        'gnd_mount',
        'weld'
    ]

    values = parameters.split('/')
    return dict(zip(keys, values))


def cost_calculation(parsed_params: Dict[str, str], series: str) -> float:
    MatCollector = MaterialCollector(series)
    total_cost = 0
    width = float(parsed_params.get('width'))/1000
    depth = float(parsed_params.get('depth'))/1000
    height = float(parsed_params.get('height'))/1000

    ral = str(parsed_params.get('ral'))
    ral_price = MatCollector.get_price_by_abbr(ral)

    shelf_type, shelf_material = parse_type_material(
        parsed_params.get('shelf_type_material'))
    shelf_type = ShelfType.get_type(shelf_type)
    shelf_count = int(parsed_params.get('shelf_count'))

    tabletop_material = str(parsed_params.get('tabletop_material'))
    tabletop_underlayment = str(parsed_params.get('tabletop_underlayment'))
    tabletop_rounding = str(parsed_params.get('tabletop_rounding'))

    border = str(parsed_params.get('border'))
    border_fold = True if parsed_params.get('border_fold') != '-' else False

    cabinet_count = int(parsed_params.get('cabinet_count')[:-1].split('('))
    cabinet_size = split_to_float(parsed_params.get('cabinet_size'), 'x')

    pillars = str(parsed_params.get('pillars'))
    pillar_wheels = str(parsed_params.get('pillar_wheels'))

    back_pillars_indent = 0.000 + \
        float(parsed_params.get('back_pillars_indent').split('.')[-1])/1000
    gnd_mount = True if str(parsed_params.get('gnd_mount')) != '-' else False
    weld = str(parsed_params.get('weld'))

    shelf_cross_cost = 0
    tabletop_cost = tabletop_calc(MatCollector, series, (width - 0.1),
                                  (depth - 0.14), tabletop_material, tabletop_underlayment)

    if border != 'борт.нет':
        border_cost = border_calc(
            MatCollector, width, depth, border, border_fold, tabletop_material)
    else:
        border_cost = 0

    if shelf_count > 0:
        shelf_cross_cost = 0
        for _ in range(shelf_count):
            shelfs_cost += calculate_table_shelf_cost(
                MatCollector, series, width, depth,
                shelf_material, shelf_type, ral_price, weld)
            shelfs_cost += (width + 0.09) * MatCollector.get_price_by_id(12)
    else:
        shelf_cross_cost = crossmember_calc(
            MatCollector, series, (width - 0.1), (depth - 0.14), shelf_type)
    if cabinet_count > 0:
        cabinet_cost = 0
        for _ in cabinet_count:
            cabinet_cost += cabinet_calc(MatCollector, series, cabinet_size)

    else:
        cabinet_cost = 0
    if tabletop_rounding != 'нет':
        total_cost += MaterialCollector.get_price_by_id('id of rounding')

    pillar_cost = pillar_calc(MatCollector, series, width, height)
    pillar_cost = pillar_cost if pillars == 'стандарт' else pillar_cost * 2
    total_cost += tabletop_cost + shelf_cross_cost + \
        pillar_cost + border_cost + cabinet_cost
    total_cost += MaterialCollector.get_price_by_abbr(pillar_wheels)
    total_cost += MaterialCollector.calculate_misc()

    return total_cost


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_params(parameters)
    cost = cost_calculation(parsed_params, series)

    return round(cost, 2)
