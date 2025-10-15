from typing import Dict
from app.data.classes import ShelfType
from app.modules.neutral_base import calculate_shelf_reinforcement, calculate_default_shelf_cost, calculate_difficulty_сoef, pillar_calc
from app.modules.material_collector import MaterialCollector


'''
Стеллажи
'''


def parse_parameters(parameters: str) -> Dict[str, str]:
    '''
    Модуль расчета стоимости разборных стеллажей
    Пример запроса в модуль:
    {
    "series": "СтПБ",
    "parameters": "600/600/1800/RAL7024/н.ст.08/-/4/СССС/усиление.нет/разборн./ст.опоры"
    }
    "parameters": "600/500/1800/н.ст.10/5/ППППП/усиление.нет/сварн"
    '''
    keys = [
        'width',
        'depth',
        'height',
        'ral_pillars',
        'material',
        'ral_shelfs',
        'shelf_count',
        'shelf_order',
        'additional_reinf',
        'isAssembled',
        'stands_type',
    ]

    values = parameters.split('/')

    if len(keys) == len(values):
        return dict(zip(keys, values))
    else:
        raise ValueError(
            'Too many/not enough parameters. Hint: Check the input parameters in `parse_parameters()` or `calculate()` functions')


def cost_calculation(parsed_params: Dict[str, str], series: str) -> float:
    # creating a class object to collect materials and prices
    mat_collector = MaterialCollector(series)
    
    total_cost = 0
    width = float(parsed_params.get('width', 0))/1000
    depth = float(parsed_params.get('depth', 0))/1000
    height = float(parsed_params.get('height', 0))/1000

    shelf_material = str(parsed_params.get('material', 'н.ст.08'))
    shelf_count = int(parsed_params.get('shelf_count', 4))
    shelf_order = str(parsed_params.get('shelfs_order', 'С' * shelf_count))

    ral_s = str(parsed_params.get('ral_shelfs', '-'))
    ral_p = str(parsed_params.get('ral_pillars', '-'))

    reinf = parsed_params.get('additional_reinf', 'усиление.нет')
    isAssembled = 'сборн.'if parsed_params.get(
        'isAssembled') == 'разборн.' else parsed_params.get('isAssembled')
    stands = parsed_params.get('stands_type')

    pillar_cost = pillar_calc(mat_collector, series,
                              width, height, ral_p)
    print(pillar_cost)

    shelfs_cost: float = 0.00
    for char in shelf_order:
        s_type = ShelfType.get_type(char)
        shelfs_cost += calculate_default_shelf_cost(
            mat_collector, width, depth,
            shelf_material, s_type,
            ral_s)
        shelfs_cost += calculate_shelf_reinforcement(
            mat_collector, width)
        if reinf == 'усиление.да':
            shelfs_cost += calculate_shelf_reinforcement(
                mat_collector, width)
    print(shelfs_cost)
    misc_cost = mat_collector.calculate_misc()
    total_cost += float(mat_collector.get_price_by_abbr(isAssembled))
    total_cost += float(mat_collector.get_price_by_abbr(stands))

    total_cost = pillar_cost + shelfs_cost + misc_cost
    # Проверить еще коэффициенты к полкам, только полкам
    return total_cost * calculate_difficulty_сoef(width, depth, shelf_material)


def calculate(parameters: str, series: str) -> float:

    parsed_params = parse_parameters(parameters)
    cost = cost_calculation(parsed_params, series)

    return round(cost, 2)
