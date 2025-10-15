from app.utils.DBrepository import DBRepository
from app.utils.handlers.request_handler import RequestHandler


def calculate(*_) -> float:

    handler = RequestHandler(dict(), dict())

    # В каждой строчке по 3 значения
    handler.list_for_request = [




    ]

    handler.list_for_request_options = []

    DBrepo = DBRepository(db_path='tests/test_data/test.db')
    handler.received_data = DBrepo.get_parameters_for_db(
        handler.list_for_request,
        list_of_column_names=["Name", "Price", "Weight"]
    )

    if handler.list_for_request_options:
        handler.received_data_options = DBrepo.get_parameters_for_db(
            handler.list_for_request_options,
            name_of_db_table="CurrentDataOption",
            list_of_column_names=["Name", "Value"],
            requered_filter="ProductionType = \'Components\'"
        )

    koeficient_of_marjinality = 0
    difficult_of_product = 0
    additional_cost = 0
    cost_of_production = 0

    cost_of_production = (
        # Двигатель                                                             |Двигатель вентилятора YZ10-20-26 (Китай)
        146 +
        147 +  # Крыльчатка                                                            |Крыльчатка пластик 200 мм /28°
        148 +  # Решетка для крыльчатки                                                |Решетка для крыльчатки 200мм 10Вт
        # Выключатель (зеленый) кнопка                                          |3INB4MASK48N1E21
        149 +
        # Трубка медная 1/4 6.35 Majdanpek (бухта 15 метров =1 единица)         |Majdanpek до 1200мм/свыше
        128 +
        128 * 0.2 +  # Труба высокого давления газовая                                 |1/4 6.35 Majdanpek
        128 * 0.1 +  # Труба высокого давления жидкостная                              |1/4 6.35 Majdanpek
        128 * 0.6 +  # Труба низкого давления                                          |1/4 6.35 Majdanpek
        150 +  # Шнур с евровилкой 3 м                                                 |Шнур с евровилкой 3 м
        167 +  # Дросселирующее устройство                                             |капилярная трубка 0,67мм
        129 +  # Термоизоляция для труб K-FLEX 2 м                                     |ST 6-06 мм
        151 +  # Клапан Шредера 6х1х100мм                                              |Клапан Шредера 6х1х100мм
        152 +  # Компрессор                                                            |Компрессор NEU2168 GK
        # Конденсатор                                                           |Конденсатор Fnt-11084301.00.000 (4-х рядный) Низкий
        153 +
        154 +  # Фильтр осушитель                                                      |Фильтр-осушитель 50 гр 6,2х6,2 DENA
        # Контроллер  Elitech ECS 961 neo                                       |Контроллер ECS-961 NEO (16A) Elitech, один датчик
        155 +
        # Кнопка подсветки                                                      |Кнопка синяя (переключатель клавишный) WR-3107 Bl 4P
        156 +
        # Регулятор скорости вращения вентилятора (-ов) воздухоохладителя (-ей) |Регулятор скорости AC двигателя KTS-A7 300 Вт, 220VAC с выключателем
        157 +
        # Штифт                                                                 |Полкодержатель круглый ф6мм (AISI304, резьба М5) L16 мм
        158 +
        159 +  # Винт М5х12                                                            |Винт М5х10 DIN7985 с цил.гол. со сферой, нерж. А2
        # Заклепка вытяжная                                                |Заклепка 4,8х8,0 (011110934808)
        160 * 20 +
        161 * 20 +  # Заклепка резьбовая М5                                            |Заклепка резьбовая М5
        162 +  # Опора металлическая                                                   |Опора металлическая ф51 H=50
        # Опора пластиковая (вставляется в металлическую)                       |Опора барная d51, чёрная
        163 +
        # Саморез                                                               |Саморез 4,2х13 сверло (А2-А-1 00001549)
        164 +
        # Блок питания 24 В                                                     |Блок питания 24V 024345 ARPV-LV24060 (4,2A;100W) IP67
        165 +
        # Скотч алюминиевый                                                     |Клейкая лента алюминиевая UNIBOB 50мм х 40м (ИУ/24)
        166 +
        # Уголок оцинкованный 19х447                           |ОЦ 08 пс 1,00 мм
        16 * 8 * 0.04 * 0.45 +
        # Уголок высота 19х400                                  |ОЦ 08 пс 1,00 мм
        16 * 4 * 0.04 * 0.4 +
        # Панель передняя( лицевая сторона) 310х450 мм             |ОЦ 08 пс 1,00 мм
        23 * 0.31 * 0.45 +
        # Панель ( боковая сторона) 400х450                     |ОЦ 08 пс 1,00 мм
        23 * 3 * 0.45 * 0.4 +
        # Панель под контроллеры 450х90                            |ОЦ 08 пс 1,00 мм
        23 * 0.45 * 0.09 +
        # Поддон под агрегат( платформа нижняя) 405х465            |ОЦ 08 пс 1,5 мм
        23 * 0.41 * 0.48 +
        # Платформа под агрегат                                     |ОЦ 08 пс сп 1,5 мм
        23 * 0.45 * 0.55
    )
    # Агрегат для витрины Glassier тип 1
    full_cost = (cost_of_production + additional_cost) * \
        (1 + koeficient_of_marjinality) * (1 + difficult_of_product)
    return round(full_cost, 2)
