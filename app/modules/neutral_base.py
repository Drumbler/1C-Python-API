from re import findall
from app.utils.custom.gusset_class import GussetType
from app.utils.custom.shelf_class import ShelfType
from app.data.material_collector import MaterialCollector


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
    '''
    Разделяет и возвращает тип и материал для обвязки или полки стола
    '''
    if shelf_type_material == 'полка.нет' or shelf_type_material == 'обвязка.3ст':
        return None, shelf_type_material
    s_type, s_mat = shelf_type_material[:-1].split('(')

    return s_type, s_mat


def calculate_default_shelf_cost(MaterialBase: MaterialCollector,
                                 width: float,
                                 depth: float,
                                 material: str | None,
                                 shelf_type: ShelfType | None,
                                 ral: str | None) -> float:
    '''
    Рассчитывает стоимость полки для стеллажа и подобных
    '''
    if not material:
        material = 'н.ст.08'
    if not shelf_type:
        shelf_type = ShelfType.STANDART
    if not ral:
        ral = '-'
    shelf_cost = MaterialBase.get_price_by_abbr(
        material) * (width + 0.09) * (depth + 0.09)
    ral_cost = (width + 0.09) * (depth + 0.09) * \
        MaterialBase.get_price_by_abbr(ral)
    match shelf_type:
        case ShelfType.PERFORATED:
            shelf_cost *= (1 + float(MaterialBase.get_price_by_id(226)))
        case ShelfType.GRILLE:
            shelf_cost += float(MaterialBase.get_price_by_id(225))
    shelf_reinforcement = calculate_shelf_reinforcement(MaterialBase, width)
    # Попробовать потом * (1 + calculate_difficulty_сoef(width, depth, material))
    return shelf_cost + ral_cost + shelf_reinforcement


def calculate_plank_racks_and_backwalls(MaterialBase: MaterialCollector,
                                        width: float,
                                        depth: float) -> float:
    '''
    Рассчитывает и возвращает стоимость задней стенки и крепежей для стеллажей для сушки досок (СтППд)
    '''
    back_wall = width * 0.170 * MaterialBase.materials.get(1)[-2]
    rack = (depth + 0.170 * MaterialBase.materials.get(283)
            [-2]) * (width // 0.015)
    return back_wall + rack


def calculate_table_shelf_cost(MaterialBase: MaterialCollector,
                               series: str,
                               width: float,
                               depth: float,
                               material: float | None,
                               shelf_type: ShelfType | str,
                               ral: float,
                               weld: str) -> float:
    '''
    Рассчитывает стоимость полки для стола
    '''
    crossmember = crossmember_calc(MaterialBase, series, width, depth, weld)
    shelf_cost = (width + 0.09) * (depth + 0.09) * \
        MaterialBase.get_price_by_abbr(material)
    match shelf_type:
        case ShelfType.PERFORATED:
            shelf_cost *= (1 + float(MaterialBase.get_price_by_id(226)))
        case ShelfType.GRILLE:
            shelf_cost += float(MaterialBase.get_price_by_id(225))
    shelf_cost += calculate_shelf_reinforcement(
        MaterialBase, width + 0.09) + crossmember
    ral_cost = (width + 0.09) * (depth + 0.09) * \
        MaterialBase.get_price_by_abbr(ral)
    return shelf_cost + ral_cost


def calculate_shelf_reinforcement(MaterialBase: MaterialCollector, width: float) -> float:
    '''
    Рассчитывает стоимость усиления полки
    '''
    return ((width + 0.09) * float(MaterialBase.get_price_by_id(12)))


# def find_series_last_char(series: str) -> str:
#     list_series = ('СтП', 'СП', 'ВМ', 'ТШ')
#     for product in list_series:
#         if product in series:
#             variation = series.replace(product, '')[0]
#             return variation
#     return None

def find_series_last_char(series: str) -> str:
    '''
    Функция для поиска последней буквы в серии, которая означает материал изделия
    '''

    TARGET_LETTERS = 'БНЛПЭСУ'
    matches = findall(r"[{}]".format(TARGET_LETTERS), series)
    return matches[-1] if matches else None


def tabletop_calc(MaterialBase: MaterialCollector,
                  series: str,
                  width: float,
                  depth: float,
                  tabletop_material: str,
                  underlayment_material: str) -> float:
    '''
    Рассчитывает стоимость столешницы для стола
    '''
    total_cost = 0
    tabletop_cost = (width + 0.090) * (depth + 0.090) * \
        float(MaterialBase.get_price_by_abbr(tabletop_material))
    # Идея: Сделать еще одну табличку для записи материалов по букве серии (id, series_id(Может FK), series_letter, mat_id(FK))
    side_apron_cost = (depth - 0.140) * 0.150 * \
        float(MaterialBase.get_price_by_abbr(find_series_last_char(series)))
    back_apron_cost = (width - 0.140) * 0.150 * \
        float(MaterialBase.get_price_by_abbr(find_series_last_char(series)))

    underlayment_cost = (width + 0.090) * depth + 0.090 * \
        float(MaterialBase.get_price_by_abbr(underlayment_material))
    total_cost += tabletop_cost + side_apron_cost + \
        back_apron_cost + underlayment_cost
    return total_cost


def border_calc(MaterialBase: MaterialCollector, width: float, depth: float, border: str, border_fold: bool, material: str):
    '''
    Рассчитывает стоимость борта для столов
    '''
    total_cost = 0
    border_type, border_sides, border_size = _define_border_type(border)
    if border_sides == '3ст':
        total_cost = 2 * (depth * border_size * MaterialBase.get_price_by_abbr(
            material)) + (width * border_size * MaterialBase.get_price_by_abbr(material))
    elif border_sides == '2ст':
        total_cost = (depth * border_size * MaterialBase.get_price_by_abbr(material)) + \
            (width * border_size * MaterialBase.get_price_by_abbr(material))
    if border_type == 'объемн.борт':
        total_cost = (width + 0.40 * border_size *
                      MaterialBase.get_price_by_abbr(material))
    if border_fold != '-':
        total_cost += width + (depth * 2) * 0.040 * \
            MaterialBase.get_price_by_abbr(material)

    return total_cost


def _define_border_type(border: str) -> list[str, str, int]:
    '''
    Определяет тип борта
    '''
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


def cabinet_calc(MaterialBase: MaterialCollector,
                 series: str,
                 sizes: list[int]
                 ) -> float:
    '''
    Рассчитывает стоимость ящика для стола
    '''
    material = MaterialBase.get_price_by_abbr(find_series_last_char(series))
    cab_width, cab_depth = sizes
    cabinet_guide = material * (cab_depth + 0.060) * 0.080
    cabinet = ((cab_width + 0.140 * 2) * (cab_depth + 0.020 * 2)) * material
    cabinet_backwall = cab_width * 0.140 * material
    cabinet_frontwall = (cab_width + 0.070) * 0.280 * material
    total_cost = cabinet_guide + cabinet + cabinet_backwall + cabinet_frontwall
    return total_cost


def pillar_calc(MaterialBase: MaterialCollector,
                series: str,
                width: float,
                height: float,
                ral: str | None) -> float:
    'Спросить у ольги по поводу 6 ножек для стеллажей'
    if not ral:
        ral = '-'
    total_cost = 0
    pillar_count = 4 if width <= 1.800 else 6
    ral_cost = (0.04 * 2) * height * MaterialBase.get_price_by_abbr(ral)
    print(MaterialBase.get_price_by_abbr(find_series_last_char(series)))
    pillar_cost = height * \
        float(MaterialBase.get_price_by_abbr(find_series_last_char(series)))
    print('ral_p cost:', ral_cost)
    total_cost += (pillar_cost + ral_cost) * pillar_count

    return total_cost


def crossmember_calc(MaterialBase: MaterialCollector,
                     series: str, width: float,
                     depth: float, weld: str,
                     crossmember_type: str | None) -> float:
    '''
    Функция для расчета стоимости поперечин стола
    '''
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

        reinforcement_corner = 0.08 * 0.08 * MaterialBase.get_price_by_abbr(
            find_series_last_char(series)) * 8

        width_harness = width * \
            MaterialBase.get_price_by_abbr(material_abbr)

        depth_harness = depth * \
            MaterialBase.get_price_by_abbr(material_abbr)
    else:
        reinforcement_corner = 0.04 * 0.04 * MaterialBase.get_price_by_abbr(
            find_series_last_char(series)) * 8

        width_harness = width - 0.05 * \
            MaterialBase.get_price_by_abbr(find_series_last_char(series))
        depth_harness = depth - 0.05 * \
            MaterialBase.get_price_by_abbr(find_series_last_char(series))
    if crossmember_type == 'обвязка.3ст':
        total_cost += width_harness + depth_harness * 2
    total_cost += reinforcement_corner
    total_cost += width_harness * 2 + depth_harness * 2
    return total_cost


def gusset_calc(MaterialBase: MaterialCollector,
                height: float,
                depth: float,
                gusset_type: GussetType | None) -> float:
    '''
    Рассчитывает стоимость одной косынки для полок консольных
    (Все еще в разработке)
    '''
    if gusset_type is None:
        gusset_type = GussetType.STANDART
    total_cost = 0
    gusset_area = (height + 0.25) * (depth + 0.25)
    total_cost += gusset_area * MaterialBase.get_price_by_id(1)
    total_cost += MaterialBase.get_price_by_id(143) * 8
    # Добавить наценки за типы косынок GussetType
    return total_cost


def find_rack_size():
    # т - 505р 600мм, 495р 700мм, 652р 800мм 727р 900мм
    # с - 332р 500мм,360р 600мм, 389р 700мм, 418р 800мм, 460р 900мм
    # п 500мм-1000мм,
    return


def calculate_difficulty_сoef(width: float, depth: float, material: str) -> float:
    '''
    Рассчитывает коэффциент наценки за сложность изготовляемого стеллажа
    '''
    criteria = [
        (width,    EASY_WIDTHS,    0.05),
        (depth,    EASY_DEPTHS,    0.05),
        (material, EASY_MATERIALS, 0.10),
    ]

    coef: float = 0.0
    for value, allowed, weight in criteria:
        if width == 1.16 and allowed in (EASY_WIDTHS, EASY_MATERIALS):
            continue
        if value in allowed:
            coef += weight
    return 1 + coef
