from app.data.DBrepository import DBrepository
from app.controllers.request_handler import RequestHandler
from app.data.database_pool import pool


def calculate(parameters: str, series: str) -> float:
    '''
    Пример запроса:
    {
    "series":"GSD"
    "parameters":"/1000/700/300/58/Ст./Ст./3000к/"
    }
    "/Ширина/Глубина/ВысотаКупола/Температурный режим/Исполнение(золото, обычное и т.д.)/Исполнение фурнитуры/Исполнение подсветки/Вкладыш"
    '''
    parameters_list = parameters.split('/')

    list_request_mapping = {
        'пена монтажная': 'Пена для термоизоляции',
        'агрегат 1': 'Агрегат для витрины Glassier тип 1',
        '2700к': 'Лента светодиодная  арт. 020517',
        '3000к': 'Лента светодиодная  арт. 020517',
        '4000к': 'Лента светодиодная  арт. 020517',
        '6000к': 'Лента светодиодная  арт. 020517',
        'RGB': 'Лента светодиодная настраеваемая арт.XXXX-1132',
        'орн': 'Орнамит, платина 15 мм',
        'гран': 'Гранитная пластина 15 мм',
        'мрам': 'Мрамор, пластина 15 мм',
        'ст. столешница': 'нерж. ст. 430 0.8 мм ЗЕРКАЛО 2К',
        'ст. поддон': 'нерж. ст. 430 0.8 мм СУПЕР-ЗЕРКАЛО 8К',
        'внешний материал': 'оц 08 пс сп 0.7 мм',
        'внутрений материал': 'оц 08 пс сп 0.7 мм',
        'материал усиление': 'нерж. ст. 430 1.5 мм шлиф',
        'материал ванна': 'нерж. ст. 430 0.8 мм',
        'испаритель': 'Испаритель TFT 1141-00.00.00 (810mm)',
        'стекло для купола и дверей': 'Стекло просветленное 8 мм',
        'золото поддон': '',
        'золото столешница': '',
        'золото ручки': '',
        'ст. ручки': 'нерж. ст. 430 0.8 мм ЗЕРКАЛО лист',
        'свет проф.': 'Швеллер 10*12*10*1.5 , П-образный, длина 2, алюминиевый (анодир.серебро) под купол',
        'дверные ролики': 'MiniShop MS31201B комплект роликов для двери без вертикального профиля',
        'подкладка столеш': 'Фанера 10 мм',
        'Клей купол': 'Ультрафиолетовый клей для стекла',
        'Напрявляющие': 'Система направляющих для Карго мини нижнего WE29.0014.01.549',
        'тейп5': 'Клейкая лента армированная, изоляционная 5 мм',
        'тейп10': 'Клейкая лента армированная, изоляционная 10 мм',
        'вентилятор испаритель': 'Вентилятор 120*120 Арт. 4656N',

        'работа корпус': 'Стоимость трудозатрат Glassier Slide Duo (корпус)',
        'работа купол': 'Стоимость трудозатрат Glassier Slide Duo (купол)',
        'работа резка': 'Стоимость трудозатрат Glassier Slide Duo (лазерная резка)',
    }

    list_request_options_mapping = {


        'наценка': 'Наценка на продукт Glassier Slide Duo',
    }

    handler = RequestHandler(list_request_mapping=list_request_mapping,
                             list_request_options_mapping=list_request_options_mapping)

    for order_number, key in enumerate(parameters_list[4:], 4):
        if order_number == 4:
            if key == '58':
                key = 'агрегат 1'
        if order_number == 5:
            if key == 'золото':
                material_bottom = handler.handle_request('золото поддон')
                material_plate = handler.handle_request('золото столешница')
                continue
            else:
                material_bottom = handler.handle_request('ст. поддон')
                material_plate = handler.handle_request('ст. столешница')
                continue
        if order_number == 6:
            if key == 'золото':
                material_door_arms_bracing = handler.handle_request(
                    'золото ручки')
                continue
            else:
                material_door_arms_bracing = handler.handle_request(
                    'ст. ручки')
                continue
        parameters_list[order_number] = handler.handle_request(key)

    cost_work_body = handler.handle_request('работа корпус')
    cost_work_dome = handler.handle_request('работа купол')
    cost_work_cutting = handler.handle_request('работа резка')
    koeficient_of_marjinality = handler.handle_request('наценка')
    material_outer = handler.handle_request('внешний материал')
    material_inner = handler.handle_request('внутрений материал')
    material_bath = handler.handle_request('материал ванна')
    material_dome = handler.handle_request('стекло для купола и дверей')
    mounting_foam = handler.handle_request('пена монтажная')
    material_bottom_edge = handler.handle_request('материал усиление')
    vaporizer_price = handler.handle_request('испаритель')
    led_profile = handler.handle_request('свет проф.')
    guides = handler.handle_request('Напрявляющие')
    clue_dome = handler.handle_request('Клей купол')
    tape_10 = handler.handle_request('тейп10')
    tape_5 = handler.handle_request('тейп5')
    lining = handler.handle_request('подкладка столеш')
    vaporizer_fan_cost = handler.handle_request('вентилятор испаритель')

    DBrepo = DBrepository(pool)

    handler.received_data = DBrepo.get_parameters_for_db(
        handler.list_for_request,
        list_of_column_names=["Name", "Price", "Weight"]
    )

    handler.received_data_options = DBrepo.get_parameters_for_db(
        handler.list_for_request_options,
        name_of_db_table="CurrentDataOption",
        list_of_column_names=["Name", "Value"],
        requered_filter="ProductionType in (\'Glassier\',\'All\')"
    )

    depth = float(((int(parameters_list[2]) + 99) // 100) * 100)/1000
    width = float(((int(parameters_list[1]) + 99) // 100) * 100)/1000
    height = float(((int(parameters_list[3]) + 99) // 100) * 100)/1000

    cost_work_body = float(handler.received_data.get(cost_work_body, [0,])[0])
    cost_work_dome = float(handler.received_data.get(cost_work_dome, [0,])[0])
    koeficient_of_marjinality = float(
        handler.received_data.get(koeficient_of_marjinality, [0,])[0])
    material_outer = float(handler.received_data.get(material_outer, [0,])[0])
    material_inner = float(handler.received_data.get(material_inner, [0,])[0])
    material_bottom = float(
        handler.received_data.get(material_bottom, [0,])[0])
    material_bottom_edge = float(
        handler.received_data.get(material_bottom_edge, [0,])[0])
    material_plate = float(handler.received_data.get(material_plate, [0,])[0])
    material_bath = float(handler.received_data.get(material_bath, [0,])[0])
    material_dome = float(handler.received_data.get(material_dome, [0,])[0])
    material_door_arms_bracing = float(
        handler.received_data.get(material_door_arms_bracing, [0,])[0])
    material_door_arms = float(
        handler.received_data.get(material_dome, [0,])[0])
    mounting_foam = float(handler.received_data.get(mounting_foam, [0,])[0])
    machine = float(handler.received_data[parameters_list[4]][0])
    led_string = float(handler.received_data.get(parameters_list[8], [0,])[0])
    vaporizer_price = float(
        handler.received_data.get(vaporizer_price, [0,])[0])
    lining = float(handler.received_data.get(lining, [0,])[0])
    led_profile = float(handler.received_data.get(led_profile, [0,])[0])
    cost_work_cutting = float(
        handler.received_data.get(cost_work_cutting, [0,])[0])
    special_bottom_material = float(
        handler.received_data.get(parameters_list[9], [0,])[0])
    clue_dome = float(handler.received_data.get(clue_dome, [0,])[0])
    guides = float(handler.received_data.get(guides, [0,])[0])
    tape_10 = float(handler.received_data.get(tape_10, [0,])[0])
    tape_5 = float(handler.received_data.get(tape_5, [0,])[0])
    vaporizer_fan_cost = float(
        handler.received_data.get(vaporizer_fan_cost, [0,])[0])
    additional_cost = 0
    cost_of_production = 0
    difficult_of_product = 0

    vaporizer_number = 2
    width_of_hands = 0.43 if width//1 <= 1 else 0.3

    cost_of_body = (
        # Столешница AISI 430 0.8 мм зеркало 8к              |Исполнение
        (width + 0.085) * (depth + 0.07) * material_plate +
        # Подкладка под столешницу Фанера 1.0 мм
        ((width - 0.08) + 2 * (depth - 0.01)) * 0.04 * lining +
        (width - 0.08) * (depth + 0.2) * material_inner +  # Внутренее дно ОЦ 0.7 мм
        # Боковина внутреннего дна ОЦ 0.7 мм
        2 * (depth - 0.09) * 0.18 * material_inner +
        # Боковина внешней стенки большая ОЦ 0.7 мм
        2 * (width - 0.05) * 0.25 * material_outer +
        # Боковина внешней стенки малая ОЦ 0.7 мм
        2 * (depth - 0.038) * 0.25 * material_outer +
        (width - 0.05) * (depth - 0.05) * material_outer +  # Дно внешнее ОЦ 0.7 мм
        # Ванна под испаритель AISI 430 0.8 мм шлиф
        (width/2 + 0.36) * 0.25 * material_bath +
        4 * 0.04 * 0.19 * material_bath +  # Опора испарителя AISI 430 0.8 мм шлиф
        2 * 0.04 * 0.19 * material_bath +  # Опора ванны AISI 430 0.8 мм шлиф
        2 * 0.21 * 0.35 * material_inner +  # Коробка вентилятора ОЦ 0.7 мм
        # Воротник AISI 430 0.8 мм зеркало 2к                                      |Исполнение
        2 * 0.41 * 0.065 * material_plate +
        # Держатели направляющих AISI 430 1.5 мм шлиф
        ((2 * 0.13 + 0.16) * (depth - 0.035)) * material_bottom_edge +
        (width - 0.11) * 0.16 * material_inner +  # Отсекатель ОЦ 0.7 мм
        (width - 0.08) * 0.17 * material_inner +  # Перегородка ОЦ 0.7 мм
        # Панель под протвень AISI 430 0.8 мм шлиф        |Исполнение
        2 * (width + 0.07) * (depth + 0.07) * material_plate +
        # Протвень AISI 430 1 мм зеркало 8к            |Исполнение
        2 * (width/2 + 0.01) * (depth + 0.05) * material_bottom +
        # Прижимная пластина AISI 430 1 мм зеркало 8к              |Исполнение
        2 * 0.08 * (width/2 + 0.022) * material_bottom +
        # Усиления протвеня AISI 430 1.5 мм шлиф
        4 * (width/2 - 0.02) * 0.011 * material_bottom_edge +
        vaporizer_number * 0.36 * 0.430 * material_inner +  # Крышка испарителя
        vaporizer_number * vaporizer_price +  # Цена испарителя
        vaporizer_number * vaporizer_fan_cost +  # Вентилятор
        # Цена запенки ванны
        (((width - 0.05) * depth * 0.25) - ((width - 0.105) * (depth - 0.1) * 0.17)) * mounting_foam +
        guides * 2 +  # Направляющие
        tape_10 +  # Изотейп 10мм
        tape_5  # Изотейп 5мм
    )
    cost_of_dome = (
        ((height - 0.615) * (width + 2 * depth) +  # Стенки купола
         width * depth +  # Крыша купола
         (height - 0.615) * (width)) * material_dome +  # Дверца купола
        2 * width_of_hands * 0.03 * material_door_arms  # Ручки
        (width + (depth * 2 + 0.999)) // 1 * (led_string + led_profile) +  # Подсветка
        clue_dome  # УФ клей
    )
    cost_of_production = (
        cost_of_dome +  # Купол
        cost_of_body +  # Корпус
        # Вкладыш на зону выкладки
        special_bottom_material * 2 * (width/2 + 0.01) * (depth + 0.05) +
        cost_work_cutting +  # Лазерная резка
        cost_work_body +  # Затраты на труд (корпус)
        # Затраты на труд (стекло 6 элементов без учета ручек)
        cost_work_dome * 5 +
        material_door_arms_bracing * 2 * 0.05 * 0.05 +
        machine  # Агрегат
    )

    full_cost = (cost_of_production + additional_cost) * \
        (1 + koeficient_of_marjinality) * (1 + difficult_of_product)
    return round(full_cost, 2)
