from app.data.DBrepository import DBrepository
from app.controllers.request_handler import RequestHandler
from app.data.database_pool import pool
# Подумать над покраской, ...


def calculate(series: str, parameters: str) -> float:
    '''
    Пример запроса:
    {
    "series":"СХСн-700-1" Где 'н' расположение агрегата, '700' это глубина, '1' количество секций
    "parameters":"500х700х850/365/812"
    }
    "ШИРИНАх?ГЛУБИНА?хВЫСОТА изделия/ширина холодильной секции/Температурный режим/"
    '''

    # Серия : [ Материал Столешницы, Материал водовода, Матерал стоек, Множитель для стоек (настрока ширины, для трубы 1), Матерал обвязки, Множитель для обвязки (настрока ширины, для трубы 1), Матерал уголков под мойку]

    parameters_list = parameters.split('/')

    width = float(
        ((int(parameters_list[0].split('х')[0]) + 99) // 100) * 100)/1000
    depth = float(
        ((int(parameters_list[0].split('х')[1]) + 99) // 100) * 100)/1000
    height = float(
        ((int(parameters_list[0].split('х')[2]) + 99) // 100) * 100)/1000

    need_welded_bath = 1
    need_one_piece_bath = 0
    shelf_special_koeficient = ''
    shelf_additional_cost = ''
    shelf_material = ''

    additional_dict_positions = {
        'оцин': 'оц 0,7 08 пс пс',
        'нерж8': 'нерж. ст. 430 0.8 мм',
        'нерж5': 'нерж. ст. 430 0.5 мм',

        # 'работа':'Ниже в строчке 116',
    }
    additional_dict_option_positions = {

        # 'наценка':'Ниже в строчке 117',
    }

    list_request_mapping = {**additional_dict_positions, }
    list_request_options_mapping = {**additional_dict_option_positions, }
    handler = RequestHandler(list_request_mapping,
                             list_request_options_mapping)

    cost_work = handler.list_for_request.append(
        f'Стоимость трудозатрат {series}')
    koeficient_of_marjinality = handler.list_for_request.append(
        f'Наценка на продукт {series}')

    for order_number, key in enumerate(parameters_list[2:], 2):

        parameters_list[order_number] = handler.handle_request(key)

    rivet1 = handler.handle_request('заклепка 1')
    rivet2 = handler.handle_request('заклепка 2')
    self_tapping_screw = handler.handle_request('саморез')
    drain_hole = parameters_list[4]
    support_unit = handler.handle_request('опорный узел')

    DBrepo = DBrepository(pool)
    handler.received_data = DBrepo.get_parameters_for_db(
        handler.list_for_request,
        list_of_column_names=["Name", "Price", "Weight"]
    )
    handler.received_data_options = DBrepo.get_parameters_for_db(
        handler.list_for_request_options,
        name_of_db_table="CurrentDataOption",
        list_of_column_names=["Name", "Value"],
        requered_filter="ProductionType in (\'Baths\',\'All\')"
    )

    material_plate = float(handler.received_data[material_plate][0])
    material_bath = float(handler.received_data[material_bath][0])
    material_leg = float(handler.received_data[material_leg][0])
    material_strapping = float(handler.received_data[material_strapping][0])
    material_angle = float(handler.received_data[material_angle][0])
    material_bracing = float(
        handler.received_data.get(material_bracing, [0,])[0])
    cost_work = float(handler.received_data.get(cost_work, [0,])[0])
    koeficient_of_marjinality = float(
        handler.received_data_options.get(koeficient_of_marjinality, [0,])[0])
    rivet1 = float(handler.received_data.get(rivet1, [0,])[0])
    rivet2 = float(handler.received_data.get(rivet2, [0,])[0])
    self_tapping_screw = float(
        handler.received_data.get(self_tapping_screw, [0,])[0])
    support_unit = float(handler.received_data.get(support_unit, [0,])[0])

    difficult_of_product = 0
    cost_of_production = 0
    additional_cost = 0

    if 'СХСн' in series:
        cost_outer_body = (
            # Задняя стенка внешнего корпуса | оц. ст. 0.7 мм
            (width - 0.06) * (height - 0.33) * material_outer_backplate +
            # Боковая стенка внешнего корпуса | н. ст. 430 0.8 мм
            2 * (depth + 0.12) * (height - 0.06) * material_outer_wall +
            # Верхняя планка-перегородка внешнего корпуса | н. ст. 430 0.8 мм
            (width - 0.10) * 0.08 * material_outer_wall +
            # Нижняя планка-перегородка внешнего корпуса | н. ст. 430 0.8 мм
            (width - 0.10) * 0.12 * material_outer_wall +
            # Межсекционная перегородка вертикальная внешнего корпуса | н. ст. 430 0.8 мм
            (width - ((number_of_sections - 1) * (width_of_section - 0.04) + 0.11 + width_of_section)) * (height_of_section + 0.5) * material_outer_wall +
            # Дно внешнего корпуса | оц. ст. 0.7 мм
            (width + 0.03) * (depth + 0.03) * material_outer_backplate
        )

        cost_inner_body = (
            # Задняя стенка внутреннего корпуса | н. ст. 430 0.5 мм
            (width - 0.09) * (height_of_section + 0.5) * material_inner_wall +
            # Боковая стенка внутреннего корпуса | н. ст. 430 0.5 мм
            2 * (depth - 0.12) * (height_of_section + 0.5) * material_inner_wall +
            # Верхняя планка-перегородка внутреннего корпуса | н. ст. 430 0.5 мм
            (width - 0.09) * 0.09 * material_inner_wall +
            # Межсекционная перегородка вертикальная внутреннего корпуса | н. ст. 430 0.5 мм
            (width - ((number_of_sections - 1) * (width_of_section - 0.04) + 0.11 + width_of_section)) * (height_of_section + 0.5) * material_inner_wall +
            # Дно внутреннего корпуса | н. ст. 430 0.5 мм
            (width - 0.06) * (depth - 0.1) * material_inner_wall
        )

        cost_of_production = (
            cost_inner_body +
            cost_outer_body +
            2 * (width_of_section + height_of_section) * number_of_sections *
            cost_h_profile  # Н-профиль до диаметру отверстий секций
        )
    else:
        width = width - 0.4

        cost_outer_body = (
            # Задняя стенка внешнего корпуса | оц. ст. 0.7 мм
            (width + 0.01) * (height - 0.1) * material_outer_backplate +
            # Боковая стенка внешнего корпуса | н. ст. 430 0.8 мм
            2 * (depth + 0.12) * (height - 0.1) * material_outer_wall +
            # Верхняя планка-перегородка внешнего корпуса | н. ст. 430 0.8 мм
            (width - 0.1) * 0.08 * material_outer_wall +
            # Нижняя планка-перегородка внешнего корпуса | н. ст. 430 0.8 мм
            (width - 0.1) * 0.9 * material_outer_wall +
            # Межсекционная перегородка вертикальная внешнего корпуса | н. ст. 430 0.8 мм
            (width - ((number_of_sections - 1) * (width_of_section - 0.04) + 0.11 + width_of_section)) * (height_of_section + 0.5) * material_outer_wall +
            # Дно внешнего корпуса | оц. ст. 0.7 мм
            (width + 0.07) * (depth - 0.08) * material_outer_backplate
        )

        cost_inner_body = (
            # Задняя стенка внутреннего корпуса | н. ст. 430 0.5 мм
            (width - 0.09) * (height_of_section + 0.5) * material_inner_wall +
            # Боковая стенка внутреннего корпуса | н. ст. 430 0.5 мм
            2 * (depth - 0.12) * (height_of_section + 0.5) * material_inner_wall +
            # Верхняя планка-перегородка внутреннего корпуса | н. ст. 430 0.5 мм
            (width - 0.09) * 0.09 * material_inner_wall +
            # Межсекционная перегородка вертикальная внутреннего корпуса | н. ст. 430 0.5 мм
            (width - ((number_of_sections - 1) * (width_of_section - 0.04) + 0.11 + width_of_section)) * (height_of_section + 0.5) * material_inner_wall +
            # Дно внутреннего корпуса | н. ст. 430 0.5 мм
            (width - 0.06) * (depth - 0.1) * material_inner_wall
        )

        cost_of_production = (
            cost_inner_body +
            cost_outer_body +
            2 * (width_of_section + height_of_section) *
            number_of_sections * cost_h_profile
        )

    full_cost = (cost_of_production + additional_cost) * \
        (1 + koeficient_of_marjinality) * (1 + difficult_of_product)
    return round(full_cost, 2)
