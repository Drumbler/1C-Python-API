from app.data.DBrepository import DBRepository
from app.controllers.request_handler import RequestHandler


def calculate(parameters: str, series: str) -> float:
    '''
    Пример запроса:
    {
    "series":"GS"
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
        'внутрений материал': 'нерж. ст. 430 0.8 мм',
        'материал усиление': 'нерж. ст. 430 1.5 мм шлиф',
        'материал ванна': 'нерж. ст. 430 0.8 мм',
        'стекло для купола и дверей': 'Стекло просветленное 8мм',
        'золото поддон': '',
        'золото столешница': '',
        'золото ручки': '',
        'ст. ручки': 'нерж. ст. 430 0.8 мм ЗЕРКАЛО лист',
        'свет проф.': 'Швеллер 10*12*10*1.5 , П-образный, длина 2, алюминиевый (анодир.серебро) под купол',
        'дверные ролики': 'MiniShop MS31201B комплект роликов для двери без вертикального профиля',
        'подкладка столеш': 'Фанера 10мм',
        'Клей купол': 'Ультрафиолетовый клей для стекла',
        'Напрявляющие': 'Система направляющих для Карго мини нижнего WE29.0014.01.549',
        'тейп5': 'Клейкая лента армированная, изоляционная 5 мм',
        'тейп10': 'Клейкая лента армированная, изоляционная 10 мм',
        'испаритель': 'Испаритель TFT 1141-00.00.00 (810mm)',
        'вентилятор испаритель': 'Вентилятор 120*120 Арт. 4656N',

        'работа корпус': 'Стоимость трудозатрат Glassier Slide (корпус)',
        'работа купол': 'Стоимость трудозатрат Glassier Slide (купол)',
        'работа резка': 'Стоимость трудозатрат Glassier Slide (лазерная резка)',
    }

    list_request_options_mapping = {


        'наценка': 'Наценка на продукт Glassier Slide',
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

    DBrepo = DBRepository()

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

    vaporizer_number = 1 if width//1.1 <= 1 else 2
    length_of_bath = 0.38 if width//1.1 < 1 else 0.84
    number_of_central_edge = 3 if width//1.1 >= 1 else 2
    width_of_fan_box = 0.74 if width//1.1 >= 1 else 1.2

    cost_of_body = (
        (width + 0.085) * (depth + 0.07) * material_plate +  # Столешница
        # Подкладка под столешницу
        ((width - 0.08) + 2 * (depth - 0.01)) * 0.04 * lining +
        (width - 0.01) * (depth + 0.06) * material_bottom +  # Протвень
        # Усиления протвеня и пластина под протвинем
        (number_of_central_edge * (depth - 0.05) * 0.11 + (width - 0.02) * 0.011 * 2 + width * (depth + 0.1)) * material_bottom_edge +
        0.09 * (width + 0.01) * material_bottom +  # Прижимная пластина
        (width - 0.1) * (depth + 0.44) * material_inner +  # Внутренее дно
        # Боковина внутреннего дна
        2 * (depth - 0.09) * 0.18 * material_inner +
        # Боковина внешней стенки малая
        2 * (depth - 0.05) * 0.25 * material_outer +
        # Боковина внешней стенки большая
        2 * (width - 0.05) * 0.25 * material_outer +
        (width - 0.05) * (depth - 0.05) * material_outer +  # Дно внешнее
        length_of_bath * 0.25 * material_bath +  # Ванна под испаритель
        2 * 0.05 * 0.185 * material_bath +  # Опора ванны
        vaporizer_number * 2 * 0.04 * 0.185 * material_bath +  # Опора испарителя
        vaporizer_number * 0.15 * 0.38 * material_outer +  # Отсекатель
        width_of_fan_box * 0.57 * material_inner +  # Коробка вентилятора
        vaporizer_number * 0.41 * 0.065 * material_inner +  # Воротник
        vaporizer_number * vaporizer_fan_cost +  # Вентилятор
        vaporizer_number * 0.36 * 0.430 * material_outer +  # Крышка испарителя
        (width - 0.05) * 0.14 * material_inner +  # Центральная перегородка
        vaporizer_number * vaporizer_price +  # Цена испарителя
        # Цена запенки ванны
        (((width - 0.05) * depth * 0.25) - ((width - 0.105) * (depth - 0.1) * 0.17)) * mounting_foam +
        guides +  # Направляющие
        tape_10 +  # Изотейп 10мм
        tape_5  # Изотейп 5мм
    )

    cost_of_dome = (
        ((height - 0.615) * (width + 2 * depth) +  # Стенки купола
         width * depth +  # Крыша купола
         (height - 0.615) * (width)) * material_dome +  # Дверца купола
        (width + depth * 2 + 0.999)//1 * (led_string + led_profile) +  # Подсветка
        0.4 * 0.03 * material_door_arms +  # Ручка
        clue_dome  # УФ клей
    )

    cost_of_production = (
        cost_of_dome +  # Купол
        cost_of_body +  # Корпус
        # Вкладыш на зону выкладки
        special_bottom_material * (width - 0.01) * (depth - 0.06) +
        cost_work_cutting +  # Лазерная резка
        cost_work_body +  # Затраты на труд (корпус)
        # Затраты на труд (стекло 6 элементов + средняя стенка)
        cost_work_dome * 5 +
        material_door_arms_bracing * 2 * 0.05 * 0.05 +
        machine  # Агрегат
    )

    full_cost = (cost_of_production + additional_cost) * \
        (1 + koeficient_of_marjinality) * (1 + difficult_of_product)
    return round(full_cost, 2)
