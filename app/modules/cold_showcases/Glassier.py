'''
Хз что решилось с полками, надо решить что делать с 'number_of_shell'
сейчас они никак не считываются но заведены в parse_parameters()
т.е. всегда считает что их 0


Поправить расчет на тип открывания W. У меня расчетов не было а значит  и стоимости работы на корпус и стелко тоже.

Не подключена функция определения мощньсти агрегата и в БД есть только 1 тип агрегат 

Не доделана логика компонентов (надо проверить все ли общее выведено из формул и добавить новые записи в 3 таблицу, в таблицу материалов добавить профиль для подсветки)
'''


from app.modules.material_collector import MaterialCollector
from app.modules.cold_showcases.calculate_aggregate_compressor import determine_compressor_power_level

def get_difficult_implementation(premium, unusual_impementation, additional_options):
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
    return positions.get((premium, unusual_impementation, additional_options), "наценка.нестанд.доп.опции")

def parse_parameters(parameters: str, series: str):
    """
    Обрабатывает входные параметры для витрин Glassier.
    """
    parameters_list = parameters.split('/')

    options = {
        'led_profile':'профиль.подсветка',
        'mounting_foam':'пена',
        'material_inner_C':'оц.ст.07',
        'material_outer_C':'нерж.ст.08',
        'material_bath_C':'нерж.ст.10',
        'material_dome':'стелко.08',
        'material_dome_doors':'стелко.05',
        'cost_work_dome_C': 'работа.стекло.C',
        'cost_work_dome_S': 'работа.стекло.S',
        'cost_work_dome_M': 'работа.стекло.M',
        'cost_work_body_C': 'работа.корпус.C',
        'cost_work_body_S': 'работа.корпус.S',
        'cost_work_body_M': 'работа.корпус.M',

        #Их нет
        'cost_work_body_W': 'работа.корпус.W',
        'cost_work_dome_W': 'работа.стекло.W',

        'min_temperature':'N',
        'type_of_doors':'C',
        'height_dome': None,
        'width': None,
        'deepth': None,
        'material_of_plate': None,
        'need_color': False,
        'material_of_door_frame': False,
        'need_plate_insert': False,
        'color_plate_insert': False,
        'light': '6000K',
        'handle_type': None,
        'handle_color': False,
        'need_logo': False,
        'temperature_combinated': False,
        'additional_options': 0,
        'unusual_implementation': 0,
        'number_of_shell': 0,
    }
    colors_of_plates = [
        'RAL9005','RAL7024','RAL7001',
        'RAL8017','RAL1013','RAL9016'
    ]
    
    if parameters_list[0] == '':
        del parameters_list[0]

    position_of_color = 4 if 'задн.ст.' in parameters else 5
    position_of_light = len(parameters_list) - 3

    for i, key in enumerate(parameters_list):
        if i == 11:
            continue
        if i == 0:
            if 'N' in key:
                if len(key) == 3 or len(key) == 4:
                    options['min_temperature'] = key[1]
                    options['temperature_combinated'] = True
                elif len(key) == 5:
                    options['min_temperature'] = key[1:3]
                    options['temperature_combinated'] = True
            else:
                if len(key) == 2 or len(key) == 3:
                    options['min_temperature'] = key[0]
                else:
                    options['min_temperature'] = key[0:2]
            continue
        elif i == 1:
            options['type_of_doors'] = key 
        elif i == 2:
            key = int(key)
            options['width'] = float(((key + 99) // 100) * 100) / 1000
            options['unusual_implementation'] = (
                                            1 if key % 100 != 0 else 0
                                        )
        elif i == 3:
            key = int(key)
            options['depth'] = float(((key + 99) // 100) * 100) / 1000
            options['unusual_implementation'] = (
                                            1 if key % 100 != 0 else 0
                                        )
        elif i == 4:
            key = int(key)
            options['height_dome'] = float(((key + 99) // 100) * 100) / 1000
            options['unusual_implementation'] = 1 if key != 400 else 0
        elif i == 5:
            options['material_of_plate'] = key 
        elif i == 6:
            if key == '-':
                key = None
            elif key not in colors_of_plates:
                key = 'RALzakaz'
                options['additional_options'] = 1
            options['needed_color'] = key
        elif i == 7:
            options['material_of_door_frame'] = key
        elif i == 8:
            if key != '-':
                options['need_plate_insert'] = key
        elif i == 9:
            if key != '-':
                options['color_plate_insert'] = key
        elif i == 10:
            options['light'] = key
            if key !='6000K':
                options['additional_options'] = 1
        elif i == 12:
            options['handle_type'] = 'ручки.' + key
            if key !='ст':
                options['additional_options'] = 1
        elif i == 13:
            if key != '-':
                options['handle_color'] = 'ручки.' + key
        elif i == 14:
            if key != '-':
                options['need_logo'] = key
    options['difficult_implementation'] = get_difficult_implementation(
        options['need_premium_zont'], options['unusual_implementation'],
        options['additional_options']
    )
    return options, series

def calculate(parameters: str, series: str)-> float:
    """
    Функция для расчета стоимости зонта, принимает данные следующего вида: 
    parameters - параметры характерные для витрины
    series - серия витрины

    Пример: 
    N58/S/1000/650/300/шлиф.ст/-/алюм.9005/MIRROR/черн/6000К/центр/ст/-/лого(заказ),
    """
    options, series = parse_parameters(parameters,series)

    material_db = MaterialCollector(series)
    components = material_db.calculate_misc()
    
    for key, value in options.items():
        exec(f"{key} = {repr(value)}")
    material_of_door_frame = material_db.get_price_by_abbr(material_of_door_frame)
    light = material_db.get_price_by_abbr(light)
    mounting_foam = material_db.get_price_by_abbr(mounting_foam)

    cost_work_dome = material_db.get_price_by_abbr(cost_work_dome)

    material_plate = material_db.get_price_by_abbr(material_plate)
    if need_color:
        material_plate += material_db.get_price_by_abbr(need_color)
    
    material_plate_insert = 0
    if need_plate_insert:
        material_plate_insert = material_db.get_price_by_abbr(need_plate_insert)
    if color_plate_insert:
        material_plate_insert += material_db.get_price_by_abbr(color_plate_insert)
    components += material_plate_insert * width * deepth


    handle_type = material_db.get_price_by_abbr(handle_type)
    if handle_color:
        handle_type += material_db.get_price_by_abbr(handle_color)
    components += handle_type * 2

    if need_logo:
        components += material_db.get_price_by_abbr(need_logo)
    
    koeficient_of_marjinality = 1 + \
        material_db.get_price_by_abbr(options['koeficient_of_marjinality'])
    
    difficult_of_product = material_db.get_price_by_abbr(options['difficult_implementation'])
    cost_of_production = 0
    additional_cost = 0

    match type_of_doors:
        case 'C':
            material_inner = material_db.get_price_by_abbr(material_inner_C)
            material_outer = material_db.get_price_by_abbr(material_outer_C)
            material_bath = material_db.get_price_by_abbr(material_bath_C)
            material_dome_doors = material_db.get_price_by_abbr(material_dome_doors)
            material_dome = material_db.get_price_by_abbr(material_dome)
            
            if temperature_combinated:
                machine
                vaporizer_number = 1 if width//1.1 <= 1 else 2
                number_of_midle_wall = 1
                offset_for_bottom = -0.2

                cost_of_body = (
                    (width + 0.05) * depth * material_plate + # Столешница                                                              |нерж. ст. 430 0,8 мм ЗЕРКАЛО лист
                    (width - offset_for_bottom) * (depth - 0.08) * material_plate + # Протвень                                         |нерж. ст. 430 0,8 мм СУПЕР-ЗЕРКАЛО 8К
                    (2 * (height) + width) * material_of_door_frame + # Рамка дверей                                               |труба 25*25 мм нерж. ЗЕРКАЛО
                    (width - 0.1) * (depth + 0.4) * material_inner + # Внутренее дно                                                    |ОЦ 08 пс сп 0,7 мм
                    2 * (depth - 0.05) * 0.16 * material_inner + # Боковина внутреннего дна                                             |ОЦ 08 пс сп 0,7 мм 
                    2 * (depth - 0.05) * 0.25 * material_outer + # Боковина внешней обшивки малая                                       |нерж. ст. 430 0,8 мм 
                    2 * (width - 0.05) * 0.25 * material_outer + # Боковина внешней обшивки большая                                     |нерж. ст. 430 0,8 мм 
                    (width - 0.05) * (depth - 0.05) * material_inner + # Дно внешнее                                                    |ОЦ 08 пс сп 0,7 мм
                    (width - 0.05) * 0.14 * material_inner + # Центральная перегородка                                                  |ОЦ 08 пс сп 0,7 мм
                    (width - 0.3) * (depth - 0.3) * material_bath + # Ванна под испаритель                                              |нерж. ст. 430 1,00 мм 
                    (((width - 0.05) * depth * 0.25) - ((width - 0.105) * (depth - 0.1) * 0.17)) * mounting_foam + # Цена запенки ванны |Пена монтажная
                    profile_top * (width + 2 * (height) + 0.999)//1 + # Сложный профиль боковой/верх 27-10                      |MiniShop MSA037 направляющая верхняя, серебро, L-3000
                    profile_bottom * ((width + 0.999)//1 ) + # Сложный профиль низ 25-10                                                |MiniShop MSA018 направляющая верхняя, серебро, L-3000
                    profile_doors * 4 + # Н-образный профиль 30-10                                                                      |MiniShop MSA017 направляющая верхняя, серебро, L-3000
                    castors_for_doors * 4 # Ролики для дверей                                                                         |MiniShop MS31201B комплект роликов для двери без вертикального профиля
                )

                cost_of_dome = (
                    ((height) * (width + (2 + number_of_midle_wall) * depth ) + # Стенки купола
                    width * depth) * material_dome + # Крыша купола
                    number_of_shell * width * depth * material_dome + # Полки в куполе 
                    2 * (height - 0.075) * (width/2 + 0.05) * material_dome_doors + # Дверцы купола
                    (width + (depth * 2 + 0.999))//1 * (light + led_profile) # Подсветка                                         |Лента светодиодная  арт. 020517 и профиль
                )
                cost_of_production = (
                    cost_of_dome + # Купол
                    cost_of_body + # Корпус
                    special_bottom_material * (width - offset_for_bottom) * (depth - 0.08) + # Вкладыш на зону выкладки
                    cost_work_body + # Затраты на труд (корпус)
                    cost_work_dome * (6 + number_of_midle_wall + number_of_shell) + # Затраты на труд (стекло 6 элементов + средняя стенка + полки)
                    material_door_arms * 2 # Ручки на дверцах купола
                )
            else:
                machine
                vaporizer_number = 1 if width <= 1.1 else 2
                number_of_midle_wall = 0
                offset_for_bottom = 0.05
                if ((width + 0.090) // 0.1 * 0.1) >= 1.6:
                    offset_for_bottom = -0.1
                    number_of_midle_wall = 1

                cost_of_body = (
                    (width + 0.05) * depth * material_plate + # Столешница                                                              |нерж. ст. 430 0,8 мм ЗЕРКАЛО лист
                    (width - offset_for_bottom) * (depth - 0.08) * material_plate + # Протвень                                         |нерж. ст. 430 0,8 мм СУПЕР-ЗЕРКАЛО 8К
                    (2 * (height) + width) * material_of_door_frame + # Рамка дверей                                               |труба 25*25 мм нерж. ЗЕРКАЛО
                    (width - 0.1) * (depth + 0.4) * material_inner + # Внутренее дно                                                    |ОЦ 08 пс сп 0,7 мм
                    2 * (depth - 0.05) * 0.16 * material_inner + # Боковина внутреннего дна                                             |ОЦ 08 пс сп 0,7 мм 
                    2 * (depth - 0.05) * 0.25 * material_outer + # Боковина внешней обшивки малая                                       |нерж. ст. 430 0,8 мм 
                    2 * (width - 0.05) * 0.25 * material_outer + # Боковина внешней обшивки большая                                     |нерж. ст. 430 0,8 мм 
                    (width - 0.05) * (depth - 0.05) * material_inner + # Дно внешнее                                                    |ОЦ 08 пс сп 0,7 мм
                    (width - 0.05) * 0.14 * material_inner + # Центральная перегородка                                                  |ОЦ 08 пс сп 0,7 мм
                    (width - 0.3) * (depth - 0.3) * material_bath + # Ванна под испаритель                                              |нерж. ст. 430 1,00 мм 
                    4.5 * mounting_foam + # Цена запенки ванны                                                                          |Пена монтажная
                    profile_top * (width + 2 * (height) + 0.999)//1 + # Сложный профиль боковой/верх 27-10                      |MiniShop MSA037 направляющая верхняя, серебро, L-3000
                    profile_bottom * ((width + 0.999)//1 ) + # Сложный профиль низ 25-10                                                |MiniShop MSA018 направляющая верхняя, серебро, L-3000
                    profile_doors * 4 + # Н-образный профиль 30-10                                                                      |MiniShop MSA017 направляющая верхняя, серебро, L-3000
                    castors_for_doors * 4 # Ролики для дверей                                                                         |MiniShop MS31201B комплект роликов для двери без вертикального профиля
                )

                cost_of_dome = (
                    ((height) * (width + (2 + number_of_midle_wall) * depth ) + # Стенки купола
                    width * depth) * material_dome + # Крыша купола
                    number_of_shell * width * depth * material_dome + # Полки в продукции 
                    2 * (height - 0.075) * (width/2 + 0.05) * material_dome_doors + # Дверцы купола
                    (width + (depth * 2 + 0.999))//1 * (light + led_profile) # Подсветка                                           |Лента светодиодная  арт. 020517 и профиль
                )
                
                cost_of_production = (
                    cost_of_dome + # Купол
                    cost_of_body + # Корпус
                    special_bottom_material * (width - offset_for_bottom) * (depth - 0.08) + # Вкладыш на зону выкладки
                    cost_work_body + # Затраты на труд (корпус)
                    cost_work_dome * (6 + number_of_midle_wall + number_of_shell) + # Затраты на труд (стекло 6 элементов + средняя стенка + полки)
                    material_door_arms * 2 # Ручки на дверцах купола
                )
        case 'S':
            if not temperature_combinated:
                machine
                vaporizer_number = 1 if width//1.1 <= 1 else 2
                length_of_bath = 0.38 if width//1.1 < 1 else 0.84
                number_of_central_edge = 3 if width//1.1 >= 1 else 2
                width_of_fan_box = 0.74 if width//1.1 >= 1 else 1.2
                
                cost_of_body = (
                    (width + 0.085) * (depth + 0.07) * material_plate + #Столешница
                    ((width - 0.08) + 2 * (depth - 0.01)) * 0.04 * lining + # Подкладка под столешницу
                    (width - 0.01) * (depth + 0.06) * material_plate + #Протвень
                    (number_of_central_edge * (depth - 0.05) * 0.11 + (width - 0.02) * 0.011 * 2 + width * (depth + 0.1)) * material_bottom_edge + #Усиления протвеня и пластина под протвинем
                    0.09 * (width + 0.01) * material_bottom + #Прижимная пластина
                    (width - 0.1) * (depth + 0.44) * material_inner + #Внутренее дно
                    2 * (depth - 0.09) * 0.18 * material_inner + #Боковина внутреннего дна
                    2 * (depth - 0.05) * 0.25 * material_outer + #Боковина внешней стенки малая
                    2 * (width - 0.05) * 0.25 * material_outer + #Боковина внешней стенки большая
                    (width - 0.05) * (depth - 0.05) * material_outer + #Дно внешнее
                    length_of_bath * 0.25 * material_bath + #Ванна под испаритель
                    2 * 0.05 * 0.185 * material_bath + #Опора ванны
                    vaporizer_number * 2 * 0.04 * 0.185 * material_bath + #Опора испарителя
                    vaporizer_number * 0.15 * 0.38 * material_outer + #Отсекатель 
                    width_of_fan_box * 0.57 * material_inner + #Коробка вентилятора
                    vaporizer_number * 0.41 * 0.065 * material_inner + #Воротник
                    vaporizer_number * 0.36 * 0.430 * material_outer + #Крышка испарителя
                    (width - 0.05) * 0.14 * material_inner + #Центральная перегородка
                    (((width - 0.05) * depth * 0.25) - ((width - 0.105) * (depth - 0.1) * 0.17)) * mounting_foam + # Цена запенки ванны
                    guides  # Направляющие
                )

                cost_of_dome = (
                    ((height) * (width + 2 * depth ) + # Стенки купола
                    width * depth + # Крыша купола
                    (height) * (width )) * material_dome + # Дверца купола
                    (width + depth * 2 + 0.999)//1 * (light + led_profile) + # Подсветка
                    0.4 * 0.03 * material_door_arms # Ручка 
                )

                cost_of_production = (
                    cost_of_dome + #Купол
                    cost_of_body + #Корпус
                    special_bottom_material * (width - 0.01) * (depth - 0.06) + #Вкладыш на зону выкладки
                    cost_work_cutting + #Лазерная резка
                    cost_work_body + #Затраты на труд (корпус)
                    cost_work_dome * 5 + #Затраты на труд (стекло 6 элементов + средняя стенка)
                    material_door_arms_bracing * 2 * 0.05 * 0.05
                )
            else:
                raise RuntimeError('Незвестен рассчет разнотемпературного исполнения.')
        case 'SD':
            if not temperature_combinated:
                machine
                vaporizer_number = 2
                width_of_hands = 0.43 if width//1 <= 1 else 0.3
                
                cost_of_body = (
                    (width + 0.085) * (depth + 0.07) * material_plate + #Столешница AISI 430 0.8 мм зеркало 8к              |Исполнение
                    ((width - 0.08) + 2 * (depth - 0.01)) * 0.04 * lining + # Подкладка под столешницу Фанера 1.0 мм
                    (width - 0.08) * (depth + 0.2) * material_inner + #Внутренее дно ОЦ 0.7 мм
                    2 * (depth - 0.09) * 0.18 * material_inner + #Боковина внутреннего дна ОЦ 0.7 мм
                    2 * (width - 0.05) * 0.25 * material_outer + #Боковина внешней стенки большая ОЦ 0.7 мм
                    2 * (depth - 0.038) * 0.25 * material_outer + #Боковина внешней стенки малая ОЦ 0.7 мм
                    (width - 0.05) * (depth - 0.05) * material_outer + #Дно внешнее ОЦ 0.7 мм
                    (width/2 + 0.36) * 0.25 * material_bath + #Ванна под испаритель AISI 430 0.8 мм шлиф
                    4 * 0.04 * 0.19 * material_bath + #Опора испарителя AISI 430 0.8 мм шлиф
                    2 * 0.04 * 0.19 * material_bath + #Опора ванны AISI 430 0.8 мм шлиф
                    2 * 0.21 * 0.35 * material_inner + #Коробка вентилятора ОЦ 0.7 мм
                    2 * 0.41 * 0.065 * material_plate + #Воротник AISI 430 0.8 мм зеркало 2к                                      |Исполнение
                    ((2 * 0.13 + 0.16) * (depth - 0.035)) * material_bottom_edge + #Держатели направляющих AISI 430 1.5 мм шлиф
                    (width - 0.11) * 0.16 * material_inner + #Отсекатель ОЦ 0.7 мм
                    (width - 0.08) * 0.17 * material_inner + #Перегородка ОЦ 0.7 мм
                    2 * (width + 0.07) * (depth + 0.07) * material_plate + #Панель под протвень AISI 430 0.8 мм шлиф        |Исполнение
                    2 * (width/2 + 0.01) * (depth + 0.05) * material_plate + #Протвень AISI 430 1 мм зеркало 8к            |Исполнение
                    2 * 0.08 * (width/2 + 0.022) * material_plate + #Прижимная пластина AISI 430 1 мм зеркало 8к              |Исполнение
                    4 * (width/2 - 0.02) * 0.011 * material_bottom_edge + #Усиления протвеня AISI 430 1.5 мм шлиф
                    vaporizer_number * 0.36 * 0.430 * material_inner + #Крышка испарителя
                    (((width - 0.05) * depth * 0.25) - ((width - 0.105) * (depth - 0.1) * 0.17)) * mounting_foam + #Цена запенки ванны
                    guides * 2  # Направляющие
                )
                cost_of_dome = (
                    ((height) * (width + 2 * depth ) + # Стенки купола
                    width * depth + #Крыша купола
                    (height) * (width)) * material_dome + #Дверца купола
                    2 * width_of_hands * 0.03 * material_door_arms # Ручки
                    (width + (depth * 2 + 0.999)) // 1 * (light + led_profile) #Подсветка
                )
                cost_of_production = (
                    cost_of_dome + #Купол
                    cost_of_body + #Корпус
                    special_bottom_material * 2 * (width/2 + 0.01) * (depth + 0.05) + #Вкладыш на зону выкладки
                    cost_work_cutting + #Лазерная резка
                    cost_work_body + #Затраты на труд (корпус)
                    cost_work_dome * 5 + #Затраты на труд (стекло 6 элементов без учета ручек)
                    material_door_arms_bracing * 2 * 0.05 * 0.05
                )
            else:
                raise RuntimeError('Незвестен рассчет разнотемпературного исполнения.')
        case 'W':
            if not temperature_combinated:
                machine

                return 0
            else:
                raise RuntimeError('Незвестен рассчет разнотемпературного исполнения.')
        case 'M':
            if not temperature_combinated:
                machine

                vaporizer_number = 1 if width//1.1 <= 1 else 2
                number_of_midle_wall = 0
                offset_for_bottom = 0.05
                if ((width + 0.090) // 0.1 * 0.1) >= 1.6:
                    offset_for_bottom = -0.1
                    number_of_midle_wall = 1

                cost_of_body = (
                    (width + 0.05) * depth * material_plate + # Столешница                                                              |нерж. ст. 430 0,8 мм ЗЕРКАЛО лист
                    (width - offset_for_bottom) * (depth - 0.08) * material_plate+ # Протвень                                         |нерж. ст. 430 0,8 мм СУПЕР-ЗЕРКАЛО 8К
                    (width - 0.1) * (depth + 0.4) * material_inner + # Внутренее дно                                                    |ОЦ 08 пс сп 0,7 мм
                    2 * (depth - 0.05) * 0.16 * material_inner + # Боковина внутреннего дна                                             |ОЦ 08 пс сп 0,7 мм 
                    2 * (depth - 0.05) * 0.25 * material_outer + # Боковина внешней обшивки малая                                       |нерж. ст. 430 0,8 мм 
                    2 * (width - 0.05) * 0.25 * material_outer + # Боковина внешней обшивки большая                                     |нерж. ст. 430 0,8 мм 
                    (width - 0.05) * (depth - 0.05) * material_inner + # Дно внешнее                                                    |ОЦ 08 пс сп 0,7 мм
                    (width - 0.05) * 0.14 * material_inner + # Центральная перегородка                                                  |ОЦ 08 пс сп 0,7 мм
                    (width - 0.3) * (depth - 0.3) * material_bath + # Ванна под испаритель                                              |нерж. ст. 430 1,00 мм 
                    vaporizer_number * vaporizer_price + # Цена испарителя (испраитель,крышка, вентилятор, стойки и т.д.)               |Испаритель Fnt-22053001.00.000-02 (TFT 2179-02) малый, шаг-6 / Испаритель TFT 1141-00.00.00 (810mm)
                    vaporizer_number * vaporizer_fan_cost + #Вентилятор                                                                 |Вентилятор 120*120 Арт. 4656N
                    (((width - 0.05) * depth * 0.25) - ((width - 0.105) * (depth - 0.1) * 0.17)) * mounting_foam  # Цена запенки ванны |Пена монтажная                                                                       |MiniShop MS31201B комплект роликов для двери без вертикального профиля

                )
                cost_of_dome = (
                    ((height) * (width + (2 + number_of_midle_wall) * depth ) + # Стенки купола
                    width * (depth/2 + 0.025)) * material_dome + #Крыша купола
                    2 * (height - 0.075 + depth/2 - 0.025) * (width/2 + 0.05) * material_dome_doors + #Дверцы купола                      |Органическое стекло 5мм
                    (width + (depth * 2 + 0.999))//1 * (light + led_profile) + # Подсветка                                           |Лента светодиодная  арт. 020517 и профиль
                    material_door_arms #Ручки дверей                                                                                    |Обычно ручки ввиде шайбы 
                )
                cost_of_production = (
                    cost_of_dome + #Купол
                    cost_of_body + #Корпус
                    special_bottom_material * (width - offset_for_bottom) * (depth - 0.08) + #Вкладыш на зону выкладки
                    cost_work_body + #Затраты на труд (корпус)
                    cost_work_dome * (6 + number_of_midle_wall + number_of_shell) #Затраты на труд (стекло 6 элементов + средняя стенка)
                )
            else:
                raise RuntimeError('Незвестен рассчет разнотемпературного исполнения.')
        case _:
            raise RuntimeError('Незвестный тип открывания')

    cost_of_production = (
        
        # Расходники из базы данных
        components
    )

    компоненты = [
        #Стабильные
        tape_10, # Изотейп 10мм
        tape_5, # Изотейп 5мм
        clue_dome,

        #Переменные
        machine,
        vaporizer_number * vaporizer_price,
        vaporizer_number * vaporizer_fan_cost,

    ]


    additional_cost = (
        
    )

    full_cost = cost_of_production * ( koeficient_of_marjinality + difficult_of_product) + additional_cost
    return round(full_cost,2)