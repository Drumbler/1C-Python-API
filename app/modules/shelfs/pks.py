from app.modules.material_collector import MaterialCollector
from app.modules.neutral_base import calculate_default_shelf_cost, gusset_calc
from app.utils.custom.gusset_class import GussetType


def parse_parameters(parameters: str) -> dict[str: any]:
    keys = [
        'width',
        'depth',
        'height',
        'rack_type',
        'border',
        'gusset_type',
        'mounts',
        'additional_railing',
    ]
    values = parameters.split('/')
    return dict(zip(keys, values))


def calculate_cost(series: str, parsed_params: dict[str: any]) -> float:
    MatCollector = MaterialCollector(series)
    width = float(parsed_params.get('width'))/1000
    depth = float(parsed_params.get('depth'))/1000
    height = float(parsed_params.get('height'))/1000
    rack_type = parsed_params.get('rack_type')
    border =  (float(parsed_params.get('border').split('(')[-1].strip(')м'))/1000) if (parsed_params.get('border') != 'борт.нет') else 0
    gusset_type = GussetType.get_type(parsed_params.get('gusset_type'))
    mounts = parsed_params.get('mounts')
    add_railing = parsed_params.get('additional_railing')

    total_cost = 0

    total_cost += calculate_default_shelf_cost(MatCollector, width + (border) * 2 , depth + border, rack_type) * 1.05
    total_cost += gusset_calc(MatCollector, height, depth, gusset_type) * 1.05
    total_cost += MatCollector.get_price_by_abbr(rack_type) # Добавить доп. аббревиатуру в mfp таблицу для изделия
    total_cost += MatCollector.calculate_misc()
    return total_cost


def calculate(series: str, parameters: str):
    parsed_params = parse_parameters(parameters)
    return calculate_cost(series, parsed_params)
