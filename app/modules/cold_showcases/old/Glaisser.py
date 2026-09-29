from app.data.DBrepository import DBrepository
from app.controllers.request_handler import RequestHandler
from app.data.database_pool import pool


def calculate(parameters: str, series: str) -> float:
    '''
    Пример запроса:
    {
    "series":"G"
    "parameters":"/1000/700/300/58/0/Ст./Ст./3000к/"
    }
    "/Ширина/Глубина/ВысотаКупола/Температурный режим/Кол-во полк/Исполнение(золото, обычное и т.д.)/Исполнение фурнитуры/Исполнение подсветки/Вкладыш"
    '''
    parameters_list = parameters.split('/')

    list_request_mapping = {
        'пена монтажная': 'Балон пены для термоизоляции',
        'агрегат 1': 'Агрегат для витрины Glassier тип 1',
        '2700к': 'Лента светодиодная  арт. 020517',
        '3000к': 'Лента светодиодная  арт. 020517',
        '4000к': 'Лента светодиодная  арт. 020517',
        '6000к': 'Лента светодиодная  арт. 020517',
        'RGB': 'Лента светодиодная настраеваемая арт.XXXX-1132',
        'орн.виб': 'Вставка для витрин ОРНАМИТА Вибрейшн',
        'орн.вол': 'Вставка для витрин ОРНАМИТА Волна',
        'зеркало': 'Вставка для витрин зеркало',
        'иск.камень': 'Вставка для витрин искусственный камень ',
        'внешний материал': 'нерж. ст. 430 0.8 мм',
        'внутрений материал': 'оц 08 пс сп 0.7 мм',
        'испаритель': 'Испаритель TFT 1141-00.00.00 (810mm)',
        'материал ванна': 'нерж. ст. 430 1мм',
        'стекло для купола': 'Стекло просветленное 8 мм',
        'стекло для дверей': 'Стекло просветленное 5 мм',
        'ст. поддон': 'нерж. ст. 430 0.8 мм СУПЕР-ЗЕРКАЛО 8К',
        'ст. столешница': 'нерж. ст. 430 0.8 мм ЗЕРКАЛО 2К',
        'ст. арка': 'труба 25*25 мм нерж. ЗЕРКАЛО',
        'ст. проф.бок и верх': 'MiniShop MSA037 направляющая верхняя, серебро, L-3000',
        'ст. проф.низ': 'MiniShop MSA018 направляющая верхняя, серебро, L-3000',
        'ст. проф.дверцы': 'MiniShop MSA017 направляющая верхняя, серебро, L-3000',
        'золото поддон': '',
        'золото столешница': '',
        'золото арка': '',
        'золото проф.бок и верх': '',
        'золото проф.низ': '',
        'золото проф.дверцы': '',
        'золото ручки': '',
        'ст. ручки': 'Ручка мебельная RC433CP.4',
        'свет проф.': 'Швеллер 10*12*10*1.5 , П-образный, длина 2, алюминиевый (анодир.серебро) под купол',
        'дверные ролики': 'MiniShop MS31201B комплект роликов для двери без вертикального профиля',
        'Клей купол': 'Ультрафиолетовый клей для стекла',
        'тейп5': 'Клейкая лента армированная, изоляционная 5мм',
        'тейп10': 'Клейкая лента армированная, изоляционная 10мм',
        'вентилятор испаритель': 'Вентилятор 120*120 Арт. 4656N',

        'работа корпус': 'Стоимость трудозатрат Glassier Coupe (корпус)',
        'работа купол': 'Стоимость трудозатрат Glassier Coupe (купол)',
    }

    list_request_options_mapping = {


        'наценка': 'Наценка на продукт Glassier Coupe',
    }

    handler = RequestHandler(list_request_mapping=list_request_mapping,
                             list_request_options_mapping=list_request_options_mapping)

    number_of_shell = 0

    for order_number, key in enumerate(parameters_list[4:], 4):
        if order_number == 4:
            if key == '58':
                key = 'агрегат 1'
        if order_number == 5:
            number_of_shell = int(key)
            continue
        if order_number == 6:
            if key == 'золото':
                material_bottom = handler.handle_request('золото поддон')
                material_plate = handler.handle_request('золото столешница')
                material_door_frame = handler.handle_request('золото арка')
                profile_top = handler.handle_request('золото проф.бок и верх')
                profile_bottom = handler.handle_request('золото проф.низ')
                profile_doors = handler.handle_request('золото проф.дверцы')
                continue
            else:
                material_bottom = handler.handle_request('ст. поддон')
                material_plate = handler.handle_request('ст. столешница')
                material_door_frame = handler.handle_request('ст. арка')
                profile_top = handler.handle_request('ст. проф.бок и верх')
                profile_bottom = handler.handle_request('ст. проф.низ')
                profile_doors = handler.handle_request('ст. проф.дверцы')
                continue
        if order_number == 7:
            if key == 'золото':
                material_door_arms = handler.handle_request('золото ручки')
                continue
            else:
                material_door_arms = handler.handle_request('ст. ручки')
                continue
        parameters_list[order_number] = handler.handle_request(key)

    cost_work_body = handler.handle_request('работа корпус')
    cost_work_dome = handler.handle_request('работа купол')
    koeficient_of_marjinality = handler.handle_request('наценка')
    material_outer = handler.handle_request('внешний материал')
    material_inner = handler.handle_request('внутрений материал')
    material_bath = handler.handle_request('материал ванна')
    material_dome = handler.handle_request('стекло для купола')
    material_dome_doors = handler.handle_request('стекло для дверей')
    mounting_foam = handler.handle_request('пена монтажная')
    vaporizer_price = handler.handle_request('испаритель')
    led_profile = handler.handle_request('свет проф.')
    castors_for_doors = handler.handle_request('дверные ролики')
    clue_dome = handler.handle_request('Клей купол')
    tape_10 = handler.handle_request('тейп10')
    tape_5 = handler.handle_request('тейп5')
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

    width = float(((int(parameters_list[1]) + 99) // 100) * 100)/1000
    depth = float(((int(parameters_list[2]) + 99) // 100) * 100)/1000
    height = float(((int(parameters_list[3]) + 99) // 100) * 100)/1000

    cost_work_body = float(handler.received_data[cost_work_body][0])
    cost_work_dome = float(handler.received_data[cost_work_dome][0])
    koeficient_of_marjinality = float(
        handler.received_data[koeficient_of_marjinality][0])
    material_outer = float(handler.received_data[material_outer][0])
    material_inner = float(handler.received_data[material_inner][0])
    material_bottom = float(handler.received_data[material_bottom][0])
    material_plate = float(handler.received_data[material_plate][0])
    material_bath = float(handler.received_data[material_bath][0])
    material_dome = float(handler.received_data[material_dome][0])
    material_dome_doors = float(handler.received_data[material_dome_doors][0])
    material_door_arms = float(handler.received_data[material_door_arms][0])
    mounting_foam = float(handler.received_data[mounting_foam][0])
    machine = float(handler.received_data[parameters_list[4]][0])
    led_string = float(handler.received_data.get(parameters_list[8], [0,])[0])
    vaporizer_price = float(handler.received_data[vaporizer_price][0])
    material_door_frame = material_plate = float(
        handler.received_data[material_door_frame][0])
    special_bottom_material = float(
        handler.received_data.get(parameters_list[9], [0,])[0])
    led_profile = float(handler.received_data[led_profile][0])
    castors_for_doors = float(handler.received_data[castors_for_doors][0])
    tape_10 = float(handler.received_data.get(tape_10, [0,])[0])
    tape_5 = float(handler.received_data.get(tape_5, [0,])[0])
    clue_dome = float(handler.received_data.get(clue_dome, [0,])[0])
    vaporizer_fan_cost = float(
        handler.received_data.get(vaporizer_fan_cost, [0,])[0])
    cost_of_production = 0
    additional_cost = 0
    difficult_of_product = 0

    vaporizer_number = 1 if width <= 1.1 else 2
    number_of_midle_wall = 0
    offset_for_bottom = 0.05
    if ((width + 0.090) // 0.1 * 0.1) >= 1.6:
        offset_for_bottom = -0.1
        number_of_midle_wall = 1

    cost_of_body = (
        # Столешница                                                              |нерж. ст. 430 0,8 мм ЗЕРКАЛО лист
        (width + 0.05) * depth * material_plate +
        # Протвень                                         |нерж. ст. 430 0,8 мм СУПЕР-ЗЕРКАЛО 8К
        (width - offset_for_bottom) * (depth - 0.08) * material_bottom +
        # Рамка дверей                                               |труба 25*25 мм нерж. ЗЕРКАЛО
        (2 * (height - 0.615) + width) * material_door_frame +
        # Внутренее дно                                                    |ОЦ 08 пс сп 0,7 мм
        (width - 0.1) * (depth + 0.4) * material_inner +
        # Боковина внутреннего дна                                             |ОЦ 08 пс сп 0,7 мм
        2 * (depth - 0.05) * 0.16 * material_inner +
        # Боковина внешней обшивки малая                                       |нерж. ст. 430 0,8 мм
        2 * (depth - 0.05) * 0.25 * material_outer +
        # Боковина внешней обшивки большая                                     |нерж. ст. 430 0,8 мм
        2 * (width - 0.05) * 0.25 * material_outer +
        # Дно внешнее                                                    |ОЦ 08 пс сп 0,7 мм
        (width - 0.05) * (depth - 0.05) * material_inner +
        # Центральная перегородка                                                  |ОЦ 08 пс сп 0,7 мм
        (width - 0.05) * 0.14 * material_inner +
        # Ванна под испаритель                                              |нерж. ст. 430 1,00 мм
        (width - 0.3) * (depth - 0.3) * material_bath +
        # Цена испарителя (испраитель,крышка, вентилятор, стойки и т.д.)               |Испаритель Fnt-22053001.00.000-02 (TFT 2179-02) малый, шаг-6 / Испаритель TFT 1141-00.00.00 (810mm)
        vaporizer_number * vaporizer_price +
        # Вентилятор                                                                 |Вентилятор 120*120 Арт. 4656N
        vaporizer_number * vaporizer_fan_cost +
        # Цена запенки ванны                                                                          |Пена монтажная
        4.5 * mounting_foam +
        # Сложный профиль боковой/верх 27-10                      |MiniShop MSA037 направляющая верхняя, серебро, L-3000
        profile_top * (width + 2 * (height - 0.615) + 0.999)//1 +
        # Сложный профиль низ 25-10                                                |MiniShop MSA018 направляющая верхняя, серебро, L-3000
        profile_bottom * ((width + 0.999)//1) +
        profile_doors * 4 +  # Н-образный профиль 30-10                                                                      |MiniShop MSA017 направляющая верхняя, серебро, L-3000
        castors_for_doors * 4 +  # Ролики для дверей                                                                         |MiniShop MS31201B комплект роликов для двери без вертикального профиля
        tape_10 +  # Изотейп 10мм
        tape_5  # Изотейп 5мм
    )

    cost_of_dome = (
        ((height - 0.615) * (width + (2 + number_of_midle_wall) * depth) +  # Стенки купола
         width * depth) * material_dome +  # Крыша купола
        number_of_shell * width * depth * material_dome +  # Полки в продукции
        # Дверцы купола
        2 * (height - 0.690) * (width/2 + 0.05) * material_dome_doors +
        # Подсветка                                           |Лента светодиодная  арт. 020517 и профиль
        (width + (depth * 2 + 0.999))//1 * (led_string + led_profile) +
        clue_dome  # УФ клей
    )

    cost_of_production = (
        cost_of_dome +  # Купол
        cost_of_body +  # Корпус
        # Вкладыш на зону выкладки
        special_bottom_material * (width - offset_for_bottom) * (depth - 0.08) +
        cost_work_body +  # Затраты на труд (корпус)
        # Затраты на труд (стекло 6 элементов + средняя стенка + полки)
        cost_work_dome * (6 + number_of_midle_wall + number_of_shell) +
        material_door_arms * 2 +  # Ручки на дверцах купола
        machine  # Агрегат
    )

    full_cost = (cost_of_production + additional_cost) * \
        (1 + koeficient_of_marjinality) * (1 + difficult_of_product)
    return round(full_cost, 2)
