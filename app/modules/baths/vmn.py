#Подумать над покраской, ...

from app.modules.material_collector import MaterialCollector
from app.modules.neutral_base import find_series_last_char
from app.data.shelf_class import ShelfType
from app.modules.neutral_base import calculate_default_shelf_cost


def define_abbr_strapping(seria: str, welded: bool) -> str:
    if (seria == "П" or seria == "Э") and welded:
        result = seria + '.обв.сварн'
    else:
        result = seria + '.обв'
    return result

def define_material_reinforce_angle(seria: str) -> str:
    REINFORCE_MATERIAL_DICT = {
        'Л': 'оц.ст.13',
        'Н': 'н.ст.15',
        'Э': 'н.ст.15',
        'П': 'н.ст.15',
        'Б': 'краш.ст.15',
    }
    return REINFORCE_MATERIAL_DICT[seria]

def parse_parameters(parameters: str, series: str):
    """
    Обрабатывает входные параметры для ванн.
    """

    MATERIAL_FOR_PLATE = 'н.ст.08'
    MATERIAL_FOR_BATH = '439.н.ст.10'
    MATERIAL_FOR_APRON = 'оц.ст.08'
    MATERIAL_FOR_BRACING = 'оц.ст.08'
    
    parameters_list = parameters.split('/')
    options = {
        'material_plate': MATERIAL_FOR_PLATE,
        'material_bath': MATERIAL_FOR_BATH,
        'material_angle': None,
        'material_bracing': MATERIAL_FOR_BRACING,
        'material_leg':'',
        'material_strap':'',
        'material_angle':'',
        'seria': None,
        'koeficient_of_marjinality': 'наценка',
        'abbr_onepiece_bath': None,
        'depth_bath': 0,
        'width_bath': None,
        'needed_color': None,
        'board_size': 0,
        'number_of_tap_hole': 0,
        'type_of_tap_hole': None,
        'type_of_drain_hole': None,
        'need_onepiece_bath': False,
        'size_onepiece_bath': None,
        'longer_plate': 0,
        'welded': False,
        'wheels': None,
        'apron': None,
        'number_of_baths': 1,
        'type_of_shelf':None,
    }
    colors_of_baths = [
        'RAL9005','RAL7024','RAL7001',
        'RAL8017','RAL1013','RAL9016'
    ]
    if 'с' in series:
        series = series.replace('с','')
        options['width_bath'] = 0.5
    position_of_shelf = len(parameters_list) - 2

    options['number_of_baths'] = int(series[-1])
    options['seria'] = series.replace('ВМ','').replace('ВК','')[0]
    #options['seria'] = find_series_last_char(series)

    for i, key in enumerate(parameters_list):
        if i == 0:
            options['width'] = ((int(key) + 99) // 100) * 100 / 1000
        elif i == 1:
            options['depth'] = ((int(key) + 99) // 100) * 100 / 1000
        elif i == 2:
            options['height'] = ((int(key) + 99) // 100) * 100 / 1000
        elif i == 3:
            if 'глуб.м.о(' in key:
                options['height_bath'] = int(key.replace('глуб.м.о(','').replace('мм)','')) / 1000
            elif 'моеч.отд.' in key:
                series = series.replace('ц','')
                options['need_onepiece_bath'] = True
                options['abbr_onepiece_bath'] = key
                options['apron'] = MATERIAL_FOR_APRON
                options.update(zip(
                    ['width_bath','depth_bath','height_bath'], 
                    list(map(lambda x: int(x) / 1000, key.replace('моеч.отд.','').split('х')))
                    ))
        elif i == 4:
            if key == 'не.краш':
                key = None
            elif key not in colors_of_baths:
                key = 'RALzakaz'
            options['needed_color'] = key
        elif 'борт.3ст(' in key:
            options['board_size'] = (options['width'] + 2 * options['depth']) * (int(key.replace('борт.3ст(','').replace('мм)','')) / 1000)
        elif 'борт.2ст.' in key:
            options['board_size'] = (options['width'] + options['depth']) * (int(key.replace('борт.2ст.слева(','').replace('борт.2ст.справа(','').replace('мм)','')) / 1000)
        elif 'борт(' in key:
            options['board_size'] = options['width'] * (int(key.replace('борт(','').replace('мм)','')) / 1000)
        elif 'объемн.борт' in key:
            options['board_size'] = options['width'] * 0.04 * 0.09
        elif 'смес(' in key:
            options['number_of_tap_hole'] = int(key.replace('смес(','').replace('шт)',''))
        elif 'отверстие.ув.полка' in key:
            options['type_of_tap_hole'] = 'отверстие.нст'
            options['longer_plate'] = 0.05
        elif 'отверстие.ст' in key or 'отверстие.нст' in key:
            options['type_of_tap_hole'] = key
        elif 'слив.' in key:    
            options['type_of_drain_hole'] = key
        elif i == position_of_shelf and key != 'полка.нет':
            if 'спл.полка(' in key:
                options['material_of_shelf'] = key.replace('спл.полка(','')[:-1]
                options['type_of_shelf'] = 'С'
            elif 'пер.полка(' in key:
                options['material_of_shelf'] = key.replace('пер.полка(','')[:-1]
                options['type_of_shelf'] = 'П'
            elif 'полка-решетка(' in key:
                options['material_of_shelf'] = key.replace('полка-решетка(','')[:-1]
                options['type_of_shelf'] = 'Р'
            elif 'обвязка.3ст' in key:
                options['material_of_shelf'] = key.replace('обвязка.3ст','')[:-1]
                options['type_of_shelf'] = 'обв3ст'
        elif key == 'сварн':
            options['welded'] = True
        elif key == 'd100' or key == 'd125' or key == 'd160' or key == 'бампер':
            options['wheels'] = key
    
    if not options['width_bath']:
        options['width_bath'] = options['width'] - 0.1
    if not options['depth_bath']:
        options['depth_bath'] = options['depth'] - 0.14 - options['longer_plate']
    
    options['material_leg'] = f'{options["seria"]}.стойк'
    options['material_strap'] = define_abbr_strapping(options['seria'], options['welded'])
    options['material_angle'] = define_material_reinforce_angle(options['seria'])
    return options, series

def calculate(parameters: str, series: str)-> float:
    """
    Функция для расчета стоимости ванны, принимает данные следующего вида: 
    parameters - параметры характерные для ванны
    series - серия ванны

    Пример: 
    '500/700/400/н.ст.08/задн.ст.ОЦИНК/не.краш/ст.фильтры/врез.выт.нет/-/без.подсв/вент.нет/сборн', 'ВМПцс-01',
    """
    options, seria = parse_parameters(parameters,series)
    series = series.replace('К','М')

    material_db = MaterialCollector('ВанныМоечные')
    components = material_db.calculate_misc()
    additional_cost = 0
    difficult_of_product = 0
    
    width = options['width']
    depth = options['depth']
    height = options['height']
    width_bath = options['width_bath']
    depth_bath = options['depth_bath']
    height_bath = options['height_bath']
    number_of_tap_hole = options['number_of_tap_hole']
    number_of_baths = options['number_of_baths']
    material_plate = material_db.get_price_by_abbr(options['material_plate'])
    material_bath = material_db.get_price_by_abbr(options['material_bath'])
    material_leg = material_db.get_price_by_abbr(options['material_leg'])
    material_strapping = material_db.get_price_by_abbr(options['material_strap'])
    material_angle = material_db.get_price_by_abbr(options['material_angle'])
    material_bracing = material_db.get_price_by_abbr(options['material_bracing'])
    need_one_piece_bath = options['need_onepiece_bath']
    plate_side = options['board_size']
    components += material_db.get_price_by_abbr(f'работа.{series}')
    koeficient_of_marjinality = 1 + \
        material_db.get_price_by_abbr(f'наценка.{series}')
    
    if options['type_of_drain_hole']:
        components += (
            material_db.get_price_by_abbr(options['type_of_drain_hole']) *
            number_of_baths
        )
    if options['type_of_shelf'] != 'обв3ст' and options['type_of_shelf']:
        material_shelf = options['material_of_shelf']
        s_type = ShelfType.get_type(options['type_of_shelf'])
        components += calculate_default_shelf_cost(
            material_db, width, depth,
            material_shelf, s_type
        )
    elif options['type_of_shelf'] == 'обв3ст':
        components -= 1 * width * material_strapping

    if need_one_piece_bath:
        components += material_db.get_price_by_abbr(options['abbr_onepiece_bath'])
    if options['type_of_tap_hole']:
        tap_hole = material_db.get_price_by_abbr(options['type_of_tap_hole'])
    else:
        tap_hole = 0
    

    need_bracing = 1 if number_of_baths != 1 else 0
    bottom_reinforcement = 1 if number_of_baths != 1 else 0

    cost_of_strapping = (
        # Обвязка лицевая
        (4 * (width - 0.08)) * material_strapping +
        # Обвязка боковая
        (4 * (depth - 0.08)) * material_strapping
    )

    cost_of_plate = (
        # Столешница
        ((width + 0.1) * (depth - depth_bath + 0.12) + 
        (depth_bath + 0.14) * 
        (width - width_bath + 0.12)) * material_plate +
        # Борт
        plate_side * material_plate +
        # Перемычка между ваннами
        int(need_one_piece_bath) * (number_of_baths - 1) * (depth_bath + 0.05) * 0.03 * material_plate
    )

    cost_of_sink = (
        # Водовод стенки
        (height_bath + 0.015) * 
        (2 * width_bath + 2 * depth_bath + 0.04) * material_bath +
        # Водовод дно
        width_bath * depth_bath * material_bath +
        # Перемычка между ваннами
        (number_of_baths - 1) * (depth_bath + 0.05) * 0.03 * material_bath
    )
    
    cost_of_production = (
        # Столешница
        cost_of_plate +
        # Сварной водовод
        int(not need_one_piece_bath) * cost_of_sink +
        # Обвязка
        cost_of_strapping +
        # Остальные компоненты (болты, работа)
        components +
        # Вкладыш (закладная)
        need_bracing * 0.24 * 0.21 * material_bracing * 4 + 
        # Ножки
        4 * (height - 0.07) * material_leg +
        # Усиление водовода
        bottom_reinforcement * (width + 0.1) * 0.25 * material_bath + 
        # Уголок под мойку
        4 * 0.13 * 0.13 * material_angle + 
        # Отверстие под смеситель
        number_of_tap_hole * tap_hole
    )

    full_cost = (
        cost_of_production * 
        (koeficient_of_marjinality + difficult_of_product + 0.1) + 
        additional_cost
    )
    
    return round(full_cost,2)