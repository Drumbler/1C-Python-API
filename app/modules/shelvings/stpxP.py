from app.utils.custom.shelf_class import Shelf_type
from app.data.material_collector import MaterialCollector
from app.modules.neutral_base import calculate_difficulty_сoef, calculate_shelf_reinforcement, calculate_default_shelf_cost, pillar_calc


def parse_params(parameters: str) -> float:
    keys = [
        'width',
        'depth',
        'height',
        'ral_pillars',
        'shelf_count',
        'plate_racks_count',
        'glass_racks_count',
        'additional_reinf',
        'isAssembled'
    ]
    
    values = parameters.split('/')
    return dict(zip(keys, values))


def cost_calculation(series: str, parsed_params: str) -> float:
    mat_collector = MaterialCollector(series)
    total_cost: float = 0

    width = float(parsed_params.get('width', 1200))/1000
    depth = float(parsed_params.get('depth', 600))/1000
    height = float(parsed_params.get('height', 1800))/1000

    ral_p = str(parsed_params.get('ral_pillars'))
    ral_p_price =  float(mat_collector.get_price_by_abbr(ral_p))

    shelf_count = int(parsed_params.get('shelf_count'))
    plate_racks_count = int(parsed_params.get('plate_racks_count'))
    glass_racks_count = int(parsed_params.get('glass_racks_count'))
    additional_reinf = int(parsed_params.get('additional_reinf'))
    isAssembled = 'сборн.'if parsed_params.get(
        'isAssembled') == 'разборн.' else parsed_params.get('isAssembled')

    shelfs_cost: float = 0
    pillar_cost: float = pillar_calc(mat_collector, series, width, height, ral_p_price)

    shelfs_cost: float = 0
    for _ in range(shelf_count):
        shelfs_cost += calculate_default_shelf_cost(
            mat_collector, width, depth,
            mat_collector.get_price_by_id(1),
            Shelf_type.STANDART
        )
        shelfs_cost += (width + 0.09) * mat_collector.get(12)[-1]
        shelf_cost += calculate_shelf_reinforcement(mat_collector, width, additional_reinf)

    for _ in range(plate_racks_count + glass_racks_count):
        total_cost += mat_collector.materials.get(282)[-1]

    misc_cost: float = mat_collector.calculate_misc()

    total_cost += float(mat_collector.get_price_by_abbr(isAssembled))
    total_cost += pillar_cost + shelfs_cost + misc_cost

    return total_cost * calculate_difficulty_сoef(width, depth, mat_collector.materials.get(1)[1])


def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_params(parameters)
    total_cost = cost_calculation(series, parsed_params)
    return round(total_cost, 2)
