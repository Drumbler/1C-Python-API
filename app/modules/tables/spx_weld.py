from app.modules.neutral_base import crossmember_calc, tabletop_calc, shelf_calc, pillar_calc, add_misc


'''
Модуль расчета сварных столов
Пример запроса в модуль: 
/Ширина/Глубина/Материал полки/Материал столешницы
'''


def parse_params(parameters: str) -> float:
    keys = {
        'width',
        'depth',
        'shelf_material',
        'tabletop_material',
    }
    values = parameters.split('/')
    return dict(zip(keys, values))


def cost_calculation(series: str, parsed_params: str) -> float:
    total_cost = 0
    shelf_cost = 0
    width = float(parsed_params['width'])/1000
    depth = float(parsed_params['depth'])/1000
    tabletop_material = str(parsed_params.get(
        'tabletop_material', 'нерж. ст. 430 0.8 мм'))
    shelf_material = str(parsed_params.get(
        'shelf_material', ''))
    tabletop_cost = tabletop_calc(series, width, depth, tabletop_material)
    harnesses_cost = crossmember_calc(series, width, depth)
    if shelf_material:
        shelf_cost = shelf_calc(series, width, depth, shelf_material)
    pillar_cost = pillar_calc(series, width)
    total_cost += tabletop_cost + shelf_cost + pillar_cost + harnesses_cost
    total_cost += add_misc(series)
    return total_cost


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_params(parameters)
    cost = cost_calculation(series, parsed_params)
    return round(cost, 2)
