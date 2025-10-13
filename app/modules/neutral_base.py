from re import findall
from app.data.classes import ShelfType
from app.modules.material_collector import MaterialCollector


EASY_WIDTHS = frozenset({
    0.6, 0.7, 0.8, 1.16,
})
EASY_DEPTHS = frozenset({
    0.3, 0.4, 0.5, 0.6, 0.7,
})
EASY_MATERIALS = frozenset({'н.ст.08'})


yes_no_dict = {
    'да': True,
    'нет': False,
}


def parse_type_material(shelf_type_material: str) -> str:
    if shelf_type_material == 'полка.нет' or shelf_type_material == 'обвязка.3ст':
        return None, shelf_type_material
    s_type, s_mat = shelf_type_material[:-1].split('(')

    return s_type, s_mat


def calculate_default_shelf_cost(material_base: MaterialCollector,
                                 width: float,
                                 depth: float,
                                 material: str | None,
                                 shelf_type: ShelfType | None,
                                 ral: str | None) -> float:
    if not material:
        material = 'н.ст.08'
    if not shelf_type:
        shelf_type = ShelfType.STANDART
    if not ral:
        ral = '-'
    shelf_cost = material_base.get_price_by_abbr(
        material) * (width + 0.09) * (depth + 0.09)
    ral_cost = (width + 0.09) * (depth + 0.09) * \
        material_base.get_price_by_abbr(ral)
    match shelf_type:
        case ShelfType.PERFORATED:
            shelf_cost *= (1 + float(material_base.get_price_by_id(226)))
        case ShelfType.GRILLE:
            shelf_cost += float(material_base.get_price_by_id(225))
    # Попробовать потом * (1 + calculate_difficulty_сoef(width, depth, material))
    return shelf_cost + ral_cost


def calculate_plank_racks_and_backwalls(material_base: MaterialCollector,
                                        width: float,
                                        depth: float) -> float:
    back_wall = width * 0.170 * material_base.materials.get(1)[-2]
    rack = (depth + 0.170 * material_base.materials.get(283)
            [-2]) * (width // 0.015)
    return back_wall + rack


def calculate_table_shelf_cost(material_base: MaterialCollector,
                               series: str,
                               width: float,
                               depth: float,
                               material: float | None,
                               shelf_type: ShelfType | str,
                               ral: float,
                               weld: str) -> float:
    crossmember = crossmember_calc(material_base, series, width, depth, weld)
    shelf_cost = (width + 0.09) * (depth + 0.09) * \
        material_base.get_price_by_abbr(material)
    match shelf_type:
        case ShelfType.PERFORATED:
            shelf_cost *= (1 + float(material_base.get_price_by_id(226)))
        case ShelfType.GRILLE:
            shelf_cost += float(material_base.get_price_by_id(225))
    shelf_cost += calculate_shelf_reinforcement(
        material_base, width + 0.09) + crossmember
    ral_cost = (width + 0.09) * (depth + 0.09) * \
        material_base.get_price_by_abbr(ral)
    return shelf_cost + ral_cost

    pass


def calculate_shelf_reinforcement(material_base: MaterialCollector, width: float) -> float:
    return ((width + 0.09) * float(material_base.get_price_by_id(12)))


# def find_series_last_char(series: str) -> str:
#     list_series = ('СтП', 'СП', 'ВМ', 'ТШ')
#     for product in list_series:
#         if product in series:
#             variation = series.replace(product, '')[0]
#             return variation
#     return None

def find_series_last_char(series: str) -> str:

    TARGET_LETTERS = 'БНЛПЭСУ'
    matches = findall(r"[{}]".format(TARGET_LETTERS), series)
    return matches[-1] if matches else None


def tabletop_calc(material_base: MaterialCollector,
                  series: str,
                  width: float,
                  depth: float,
                  tabletop_material: str,
                  underlayment_material: str) -> float:
    total_cost = 0
    tabletop_cost = (width + 0.090) * (depth + 0.090) * \
        float(material_base.get_price_by_abbr(tabletop_material))
    # Идея: Сделать еще одну табличку для записи материалов по букве серии (id, series_id(Может FK), series_letter, mat_id(FK))
    side_apron_cost = (depth - 0.140) * 0.150 * \
        float(material_base.get_price_by_abbr(find_series_last_char(series)))
    back_apron_cost = (width - 0.140) * 0.150 * \
        float(material_base.get_price_by_abbr(find_series_last_char(series)))

    underlayment_cost = (width + 0.090) * depth + 0.090 * \
        float(material_base.get_price_by_abbr(underlayment_material))
    total_cost += tabletop_cost + side_apron_cost + \
        back_apron_cost + underlayment_cost
    return total_cost


def border_calc(material_base: MaterialCollector, width: float, depth: float, border: str, border_fold: bool, material: str):
    total_cost = 0
    border_type, border_sides, border_size = define_border_type(border)
    if border_sides == '3ст':
        total_cost = 2 * (depth * border_size * material_base.get_price_by_abbr(
            material)) + (width * border_size * material_base.get_price_by_abbr(material))
    elif border_sides == '2ст':
        total_cost = (depth * border_size * material_base.get_price_by_abbr(material)) + \
            (width * border_size * material_base.get_price_by_abbr(material))
    if border_type == 'объемн.борт':
        total_cost = (width + 0.40 * border_size *
                      material_base.get_price_by_abbr(material))
    if border_fold != '-':
        total_cost += width + (depth * 2) * 0.040 * \
            material_base.get_price_by_abbr(material)

    return total_cost


def define_border_type(border: str):
    size_int = 0
    border_type, size = border.split('(')
    size = size.strip('мм)')
    size_int = int(size)
    if border == 'объемн.борт':
        size = 45.00
    border_list: list = border_type.split('.')
    border_sides: str
    if '3ст' in border_list:
        border_sides = '3ст'
    elif '2ст' in border_list:
        border_sides = '2ст'

    return [border_type, border_sides, size_int]


def cabinet_calc(material_base: MaterialCollector,
                 series: str,
                 sizes: list[int]
                 ):
    material = material_base.get_price_by_abbr(find_series_last_char(series))
    cab_width, cab_depth = sizes
    cabinet_guide = material * (cab_depth + 0.060) * 0.080
    cabinet = ((cab_width + 0.140 * 2) * (cab_depth + 0.020 * 2)) * material
    cabinet_backwall = cab_width * 0.140 * material
    cabinet_frontwall = (cab_width + 0.070) * 0.280 * material
    total_cost = cabinet_guide + cabinet + cabinet_backwall + cabinet_frontwall
    return total_cost


def pillar_calc(material_base: MaterialCollector,
                series: str,
                width: float,
                height: float,
                ral: str | None) -> float:
    'Спросить у ольги по поводу 6 ножек для стеллажей'
    if not ral:
        ral = '-'
    total_cost = 0
    pillar_count = 4 if width <= 1.800 else 6
    ral_cost = (0.04 * 2) * height * material_base.get_price_by_abbr(ral)
    print(find_series_last_char(series))
    print(material_base.get_price_by_abbr(find_series_last_char(series)))
    pillar_cost = height * \
        float(material_base.get_price_by_abbr(find_series_last_char(series)))
    print('pillar cost:', pillar_cost)
    print('ral cost:', ral_cost)
    print(total_cost)
    total_cost += (pillar_cost + ral_cost) * pillar_count

    return total_cost


def crossmember_calc(material_base: MaterialCollector,
                     series: str, width: float,
                     depth: float, weld: str,
                     crossmember_type: str | None) -> float:
    total_cost = 0
    material_abbr = find_series_last_char(series)
    if weld == 'сварн':
        material_abbr = weld + material_abbr
    pipe_series = {
        'СТП',
        'СТЭ'
    }
    total_cost = 0
    if series in pipe_series:

        reinforcement_corner = 0.08 * 0.08 * material_base.get_price_by_abbr(
            find_series_last_char(series)) * 8

        width_harness = width * \
            material_base.get_price_by_abbr(material_abbr)

        depth_harness = depth * \
            material_base.get_price_by_abbr(material_abbr)
    else:
        reinforcement_corner = 0.04 * 0.04 * material_base.get_price_by_abbr(
            find_series_last_char(series)) * 8

        width_harness = width - 0.05 * \
            material_base.get_price_by_abbr(find_series_last_char(series))
        depth_harness = depth - 0.05 * \
            material_base.get_price_by_abbr(find_series_last_char(series))
    if crossmember_type == 'обвязка.3ст':
        total_cost += width_harness + depth_harness * 2
    total_cost += reinforcement_corner
    total_cost += width_harness * 2 + depth_harness * 2
    return total_cost


def gusset_calc(series, height, depth) -> float:
    total_cost = 0

    # total_cost = (height + GUSSET_CUT[series]['height']) * (
    #     depth + GUSSET_CUT[series]['depth']) * material_prices['нерж.ст. 430 0.8мм']
    return total_cost


def find_rack_size():
    # т - 505р 600мм, 495р 700мм, 652р 800мм 727р 900мм
    # с - 332р 500мм,360р 600мм, 389р 700мм, 418р 800мм, 460р 900мм
    # п 500мм-1000мм,
    pass


def calculate_difficulty_сoef(width: float, depth: float, material: str) -> float:
    criteria = [
        (width,    EASY_WIDTHS,    0.05),
        (depth,    EASY_DEPTHS,    0.05),
        (material, EASY_MATERIALS, 0.10),
    ]

    coef = 0.0
    for value, allowed, weight in criteria:
        if width == 1.16 and allowed in (EASY_WIDTHS, EASY_MATERIALS):
            continue
        if value in allowed:
            coef += weight
    return 1 + coef
