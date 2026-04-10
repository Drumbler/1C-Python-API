from app.modules.material_collector import MaterialCollector
from app.modules.zvn_base import calculate_body
from app.utils.custom.ZVNseries_class import ZVNSeries

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
                                 premium, unusual_impementation, 
                                 additional_options, series: str) -> float:
    markup: float = 0.00
    if '04' in series: 
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

def parse_parameters(parameters: str) -> dict[str, str]:

    keys = [
        '0',
        'width',
        'depth',
        'height',
        'body_material',
        'backplate_material',
        'RAL',
        'filters',
        'main_cut_out',
        'add_cut_out',
        'main_cut_in',
        'add_cut_in',
        'lights',
        'fan',
        'weld',
        'is_CUBE'
    ]

    values = parameters.split('/')
    if values[0]:
        del values[0]
        parsed_params = dict(zip(keys, values))
        parsed_params[-1] = 'CUBE'
    else:
        parsed_params[-1] = '0'
        parsed_params = dict(zip(keys, values))

    return parsed_params

def cost_calculation(parsed_params: dict[str, str], series: str) -> float:
    formatted_series = ZVNSeries(series)

    MatCollector = MaterialCollector(series)
    total_cost = 0
    width = parsed_params.get('width')/1000
    depth = parsed_params.get('depth')/1000
    height = parsed_params.get('height')/1000
    body_material = parsed_params.get('body_material')
    backplate_material = parsed_params.get('backplate_material')
    ral = parsed_params.get('RAL')
    filters = parsed_params.get('filters')
    main_cut_out = parsed_params.get('main_cut_out')
    add_cut_out = parsed_params.get('add_cut_out')
    main_cut_in = parsed_params.get('main_cut_in')
    add_cut_in = parsed_params.get('add_cut_in')
    lights = parsed_params.get('lights')
    fan = parsed_params.get('fan')
    weld = parsed_params.get('weld')
    is_CUBE = parsed_params.get('is_CUBE')

    body_cost = calculate_body(MatCollector, 
                               series, 
                               width, 
                               depth, 
                               height,
                               body_material,
                               backplate_material,
                               ral)
    






def calculate(parameters: str, series: str) -> float:


    



