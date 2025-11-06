from app.modules.material_collector import MaterialCollector

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
    JU200 = ((0.059*0.57) * 5 + (0.19*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 100 # Стоимость трудозатрат 100 рублей (по хорошему отдельная переменная на вход)
    JU300 = ((0.059*0.57) * 7 + (0.29*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 100
    JU400 = ((0.059*0.57) * 9 + (0.39*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 100
    JU500 = ((0.059*0.57) * 11 + (0.49*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 100
    JU600 = ((0.059*0.57) * 15 + (0.59*0.053) * 4 + (0.58*0.053) * 4 + (0.06*0.08) * 2) * material + 100
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

def parse_parameters(parameters: str, series: str):
    """
    Обрабатывает входные параметры для зонтов.
    """
    parameters_list = parameters.split('/')

    if '04' in series:
        min_width, max_width, min_depth, max_depth = [500, 2200, 1200, 2200]
    else:
        min_width, max_width, min_depth, max_depth = [500, 2200, 500, 1400]
        if '01' in series:
            max_depth = 700

    options = {
        'need_cube_zont': None,
        'need_premium_zont': 0,
        'additional_options': 0,
        'unusual_implementation': 0,
        'need_premium_filter': None,
        'need_filter': 1,
        'need_spark_arrester': None,
        'needed_color': None,
        'number_torchs': 0,
        'need_cuthole': None,
        'need_fan': None,
        'material_nerj': 'н.ст.08',
        'material_ocin': 'оц.ст.08',
        'faucet': 'кран.сливной',
        'koeficient_of_marjinality': 'наценка',
        'difficult_implementation': None,
    }
    colors_of_zonts = [
        'RAL9005','RAL7024','RAL7001',
        'RAL8017','RAL1013','RAL9016'
    ]
    
    if parameters_list[0] == 'CUBE':
        del parameters_list[0]
        options['unusual_implementation'] = 1
        options['need_cube_zont'] = 'CUBE'
    elif '03' in series and parameters_list[0] == '':
        del parameters_list[0]
    if ' ПРЕМИУМ' in series:
        options['need_premium_zont'] = 1
        series = series.replace(' ПРЕМИУМ','')

    position_of_color = 4 if 'задн.ст.' in parameters else 5
    position_of_light = len(parameters_list) - 3

    for i, key in enumerate(parameters_list):
        if key == 'сборн' or key == 'разборн':
            continue 
        if i == 0:
            key = int(key)
            options['width'] = float(((key + 99) // 100) * 100) / 1000
            options['unusual_implementation'] = (
                                            1 if (
                                                (key < min_width or key > max_width)
                                                or key % 100 != 0
                                            ) else 0
                                        )
        elif i == 1:
            key = int(key)
            options['depth'] = float(((key + 99) // 100) * 100) / 1000
            options['unusual_implementation'] = (
                                            1 if (
                                                (key < min_depth or key > max_depth)
                                                or key % 100 != 0
                                            ) else 0
                                        )
        elif i == 2:
            key = int(key)
            options['height'] = float(((key + 99) // 100) * 100) / 1000
            options['unusual_implementation'] = 1 if key != 400 else 0
        elif i == 3:
            options['material'] = key
            options['material_of_backplate'] = key
        elif key == 'задн.ст.ОЦИНК':
            options['material_of_backplate'] = 'оц.ст.08'          
        elif key == 'без.фильтр':
            options['need_filter'] = 0
        elif key == 'искрогас':
            options['need_filter'] = 0
            options['need_spark_arrester'] = key
            options['additional_options'] = 1
        elif key == 'премиум.жир':
            options['need_premium_filter'] = key
            options['additional_options'] = 1
        elif  'врез.доп.выт' in key or 'врез.доп.прит' in key:
                key = 'зонт.врезка.прям'
                options['need_cuthole'] = key
                options['difficult_implementation'] = 1
                continue 
        elif  'встр.вент' in key:
                key = 'зонт.встр.вент'
                options['need_fan'] = key
                options['additional_options'] = 1
                continue
        elif i == position_of_light and key != 'без.подсв':
            if 'шт)' in key:
                key = key.replace('шт)','')
                options['number_torchs'] = ''
                for _ in range(len(key)):
                    if key[-1] == '(':
                        key = key[:-1]
                        options['need_torchs'] = key
                        break
                    options['number_torchs'] = key[-1] + options['number_torchs']
                    key = key[:-1]
            else:
                options['number_torchs'] = options['width'] - 0.1
                options['need_torchs'] = key
            options['additional_options'] = 1
        elif i == position_of_color:
            if key == 'не.краш':
                key = None
            elif key not in colors_of_zonts:
                key = 'RALzakaz'
                options['additional_options'] = 1
            options['needed_color'] = key
    options['difficult_implementation'] = get_difficult_implementation(
        MaterialCollector(series),
        options['need_premium_zont'], options['unusual_implementation'],
        options['additional_options'], series
    )
    return options, series

def calculate(parameters: str, series: str)-> float:
    """
    Функция для расчета стоимости зонта, принимает данные следующего вида: 
    parameters - параметры характерные для зонта
    series - серия зонта

    Пример: 
    '500/700/400/н.ст.08/задн.ст.ОЦИНК/не.краш/ст.фильтры/врез.выт.нет/-/без.подсв/вент.нет/сборн', 'ЗВН-01',
    """
    options, series = parse_parameters(parameters,series)

    material_db = MaterialCollector(series)
    components = material_db.calculate_misc()
    
    width = options['width']
    depth = options['depth']
    height = options['height']
    material = material_db.get_price_by_abbr(options['material'])
    material_of_backplate = material_db.get_price_by_abbr(options['material_of_backplate'])
    material_nerj = material_db.get_price_by_abbr(options['material_nerj'])
    material_ocin = material_db.get_price_by_abbr(options['material_ocin'])
    faucet = material_db.get_price_by_abbr(options['faucet'])
    
    koeficient_of_marjinality = 1 + \
        material_db.get_price_by_abbr(options['koeficient_of_marjinality'])
    
    if options['need_cube_zont']:
        koeficient_of_marjinality *= \
        (1 + material_db.get_price_by_abbr(options['need_cube_zont']))

    if options['needed_color']:
        material += material_db.get_price_by_abbr(options['needed_color'])
        material_of_backplate += material_db.get_price_by_abbr(options['needed_color'])
    
    if options['need_premium_filter']:
        options['need_premium_filter'] = 1 + material_db.get_price_by_abbr(options['need_premium_filter'])
    else:
        options['need_premium_filter'] = 1
    if options['need_spark_arrester']:
        options['need_spark_arrester'] = ((width + 0.49)//0.5) * \
            material_db.get_price_by_abbr(options['need_spark_arrester'])
    else:
        options['need_spark_arrester'] = 0
    if options['number_torchs'] != 0:
        options['need_torchs'] = float(options['number_torchs']) * \
            material_db.get_price_by_abbr(options['need_torchs'])
    else:
        options['need_torchs'] = 0
    options['need_cuthole'] = 0 if not options['need_cuthole'] else material_db.get_price_by_abbr(options['need_cuthole'])
    need_fan = 0 if not options['need_fan'] else material_db.get_price_by_abbr(options['need_fan'])
    
    
    difficult_of_product = options['difficult_implementation']
    cost_of_production = 0
    additional_cost = 0
    
    
    # Находим стоимость жироуловителей в зонте
    cost_of_filters = min_cost_to_fill(width, material_nerj)
    
    #Стоимость рассекателей, это особенность ЗПВН (приточно-вытяжных)
    if 'П' in series: 
        divider_cost = ((0.035*0.57) * 3 + (0.15*0.055) * 2 + (0.58*0.055) * 2) * material_nerj + 100
        if '04' in series:
            divider_cost *= 2
    else:
        divider_cost = 0

    if series == "ЗПВН-01" or series == "ЗВН-01" or \
        series == "ЗПВН-04/01" or series == "ЗВН-04/01" or \
        series == "ЗПВН-02" or series == "ЗВН-02" or \
        series == "ЗПВН-04/02" or series == "ЗВН-04/02":
        if '04' in series:
            square_of_product = (
                # Площадь на уклоне зонта
                2 * pow((pow((height - 0.1), 2) + pow((depth/2)-0.1, 2)), 0.5) * 0.4 +
                # Площадь части над уклоном зонта
                2 * 0.2 * (width + 0.05) +
                # Площадь крышки
                (width + 0.05) * (depth + 0.035) +
                # Боковые панели
                2 * (depth * height - 2 * 0.5 * ((height-0.1) * ((depth/2)-0.1)) + 4 * 0.05 * 0.1) 
            )
        else:
            square_of_product = (
                # Площадь на уклоне зонта
                pow((pow((height - 0.1) ,2) + pow(depth - 0.1 ,2)) ,0.5) * 0.4 +
                # Площадь части над уклоном зонта
                0.2 * (width + 0.05) +
                # Площадь "потолка" зонта
                (width + 0.05) * (depth + 0.035) +
                # Боковые панели
                2 * (depth * height - 0.5 * ((height - 0.1) * (depth - 0.1)) + 2 * 0.01 * 0.1)
            )
        if '01' in series:
            if 'П' in series: 
                individual_cost_of_production = (
                    (width - 0.005) * 0.20 * material # Полка
                )
            else: 
                individual_cost_of_production = 0
        else:
            if 'П' in series: 
                individual_cost_of_production = (
                    # Полка
                    (width - 0.005) * 0.17 * material +
                    # Приток 
                    (width - 0.005) * (height + 0.3) * material
                )
            else: 
                individual_cost_of_production = width * 0.17 * material  # Полка     
    elif series == "ЗПВН-03" or series == "ЗВН-03" or \
        series == "ЗПВН-04/03" or series == "ЗВН-04/03" or \
        series == "ЗПВН-05" or series == "ЗВН-05" or \
        series == "ЗПВН-04/05" or series == "ЗВН-04/05":
        if '04' in series:
            if depth/2 < 1:
                x = 0.13
            elif depth/2 == 1:
                x = 0.3
            else:
                x = 0.35
            square_of_product = (
                2 * pow((pow((height - 0.1),2) + pow(x,2)),0.5) * width + # Площадь на уклоне зонта
                2 * 0.12 * width + # Площадь части под уклоном зонта
                width * (depth- 2 * x + 0.04) + # Площадь "потолка" зонта
                4 * (depth/2 * height - 0.5 * ((height-0.1)*x) + 0.03 * depth/2 + 0.02 * (depth/2-x)) # Боковые панели
            )
        else:
            if depth < 1:
                x = 0.13
            elif depth == 1:
                x = 0.3
            else:
                x = 0.35
            square_of_product = (
                pow((pow((height - 0.1),2) + pow(x,2)),0.5) * width + # Площадь на уклоне зонта
                0.12 * width + # Площадь части под уклоном зонта
                width * (depth-x + 0.04) + # Площадь "потолка" зонта
                2 * ((depth + 0.05) * (height + 0.05) - 0.5 * ((height-0.1) * x)) # Боковые панели
            )
        if '05' in series:
            if '04' in series:
                square_of_product += (
                    2 * ((depth + 0.05) * (height + 0.05) - ((height-0.1) * 0.1) - (depth / 2 - 0.1) * (height - 0.2))-
                    2 * ((depth + 0.05) * (height + 0.05) - 0.5 * ((height-0.1)*x))
                )
            else:
                square_of_product += (
                    2 * ((depth + 0.05) * (height + 0.05) -  0.5 * (0.1 * 0.1) - 0.5 * (depth - 0.1) * (height - 0.2)) - 
                    2 * ((depth + 0.05) * (height + 0.05) - 0.5 * ((height-0.1)*x))
                    )
        if 'П' in series: 
            individual_cost_of_production = (
                # Полка
                (width - 0.005) * 0.17 * material + 
                # Приток
                (width - 0.005) * (height + 0.3) * material 
            )
        else: 
            individual_cost_of_production = width * 0.17 * material # Полка

    cost_of_production = (
        # Патрубок
        (0.8 * 0.75) * material_ocin +
        # Жироуловители умноженные на коэффициент прогрешности
        cost_of_filters * 1.1 * options['need_filter'] * options['need_premium_filter'] +
        # Цена задней панели
        height * (width + 0.01) * material_of_backplate + 
        # Цена остального корпуса
        square_of_product * material +
        # Ванна
        width * 0.3 * material +
        # Cливной кран
        faucet * (width + 1.05)//1.1 +
        # Цена подвесов
        (0.17 * 0.08) * 4 * material_nerj +
        # Уникальные особенности каждой серии
        individual_cost_of_production +
        # Рассекатели (ставятся по одному на каждые 400мм)
        divider_cost * ((depth + 0.39)//0.4) +
        # Расходники из базы данных
        components
    )
    if "04" in series:
        cost_of_production += (
            # Жироуловители умноженные на коэффициент прогрешности
            cost_of_filters * 1.1 * options['need_filter'] * options['need_premium_filter'] +
            # Ванна
            width * 0.15 * material +
            # Уникальные особенности каждой серии
            individual_cost_of_production -
            # Цена задней панели
            height * (width + 0.01) * material_of_backplate
        )

    additional_cost = (
        options['need_torchs'] +
        options['need_spark_arrester'] +
        options['need_cuthole'] + 
        need_fan
    )
    print(koeficient_of_marjinality, 'маржинальность')
    print(difficult_of_product, 'сложность')

    full_cost = cost_of_production * ( koeficient_of_marjinality + difficult_of_product) + additional_cost
    return round(full_cost,2)