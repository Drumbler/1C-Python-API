import re
from dataclasses import dataclass
from typing import Callable

from app.data.dto.zvn_dto import ZPVNParams, ZVNParams
from app.data.material_collector import MaterialCollector
from app.modules.zonts.filter_calculation import calculate_filters_cost
from app.utils.custom.ZVNformula_class import ZVNFormula
from app.utils.custom.ZVNseries_class import ZVNSeries


BODY_WIDTH_CLEARANCE = 0.005
SIDE_PANEL_DEPTH_ALLOWANCE = 0.015
BACK_PANEL_HEIGHT_ALLOWANCE = 0.015
TOP_PANEL_SPLIT_WIDTH_LIMIT = 1.250
TOP_PANEL_SPLIT_OVERLAP = 0.020
BATH_DEPTH = 0.300
SHELF_DEPTH = 0.170
BRANCH_PIPE_AREA = 0.8 * 0.075


@dataclass(frozen=True, slots=True)
class ZVNBody01_02Config:
    side_panel_height_allowance: float
    top_panel_depth_allowance: float
    has_shelf: bool = False
    split_top_panel: bool = False


BODY_01_02_CONFIGS = {
    '01': ZVNBody01_02Config(
        side_panel_height_allowance=0.035,
        top_panel_depth_allowance=0.165,
    ),
    '02': ZVNBody01_02Config(
        side_panel_height_allowance=0.043,
        top_panel_depth_allowance=0.135,
        has_shelf=True,
        split_top_panel=True,
    ),
}


def detect_formula(Series: ZVNSeries):
    return Series.formula


def detect_calculation_route(Series: ZVNSeries) -> tuple[bool, ZVNFormula]:
    return Series.is_island, detect_formula(Series)


def get_01_02_config(Series: ZVNSeries) -> ZVNBody01_02Config:
    config = BODY_01_02_CONFIGS.get(Series.model)
    if config is None:
        raise ValueError(f'Unsupported 01/02 model: {Series.model}')
    return config


def get_clear_body_width(width: float) -> float:
    return max(width - BODY_WIDTH_CLEARANCE, 0)


def calculate_top_panel_area_01_02(
        config: ZVNBody01_02Config,
        clear_body_width: float,
        depth: float) -> float:
    top_panel_depth = depth + config.top_panel_depth_allowance

    # Для глубоких 02 серий крышка раскраивается на две детали по шаблону из Excel.
    if config.split_top_panel and top_panel_depth > TOP_PANEL_SPLIT_WIDTH_LIMIT:
        split_tail_depth = top_panel_depth - TOP_PANEL_SPLIT_WIDTH_LIMIT + TOP_PANEL_SPLIT_OVERLAP
        return (
            clear_body_width * TOP_PANEL_SPLIT_WIDTH_LIMIT +
            clear_body_width * split_tail_depth
        )

    return clear_body_width * top_panel_depth


def calculate_01_02(
        Series: ZVNSeries, 
        MaterialBase: MaterialCollector, 
        params: ZVNParams | ZPVNParams) -> float:
    config = get_01_02_config(Series)
    body_material_price = MaterialBase.get_price_by_abbr(params.body_material)
    backplate_material_price = MaterialBase.get_price_by_abbr(params.backplate_material)
    clear_body_width = get_clear_body_width(params.width)

    back_panel = 0
    shelf = 0
    if not Series.has_supply:
        side_panel = (params.depth + SIDE_PANEL_DEPTH_ALLOWANCE) * \
                     (params.height + config.side_panel_height_allowance) * \
                     body_material_price
        top_panel = calculate_top_panel_area_01_02(
            config,
            clear_body_width,
            params.depth,
        ) * body_material_price
        back_panel = clear_body_width * \
                     (params.height + BACK_PANEL_HEIGHT_ALLOWANCE) * \
                     backplate_material_price
        bath = clear_body_width * BATH_DEPTH * body_material_price
    else:
        side_panel = 2 * ((params.depth / 2) + SIDE_PANEL_DEPTH_ALLOWANCE) * \
                     (params.height + config.side_panel_height_allowance) * \
                     body_material_price
        top_panel = calculate_top_panel_area_01_02(
            config,
            clear_body_width,
            params.depth,
        ) * body_material_price
        # back_panel = (params.width) * \
        #              (params.height + 0.015) * \
        #              MaterialBase.get_price_by_abbr(params.backplate_material)
        bath = clear_body_width * BATH_DEPTH * body_material_price

    if config.has_shelf:
        shelf = clear_body_width * SHELF_DEPTH * body_material_price

    branch_pipe = BRANCH_PIPE_AREA * backplate_material_price
    faucet = MaterialBase.get_price_by_id(124)
    
    total_cost = 2 * side_panel + top_panel + \
                 back_panel + bath + shelf + branch_pipe + faucet
    print(side_panel, 'side panel')
    print(top_panel, 'top panel')
    print(back_panel, 'back panel')
    print(bath, 'bath')
    print(shelf, 'shelf')
    print(branch_pipe, 'branch_pipe')
    print(total_cost, 'total body')
    print(faucet, 'faucet')
    return total_cost


def calculate_03_05(
        Series: ZVNSeries,
        MaterialBase: MaterialCollector,
        params: ZVNParams | ZPVNParams) -> float:
    
    back_panel = 0

    if not Series.has_supply:
        side_panel = (params.width + 0.015) * \
                     (params.height + 0.045) * \
                     (MaterialBase.get_price_by_abbr(params.body_material))
        top_panel = params.width * \
                    (params.depth + 0.250) * \
                    (MaterialBase.get_price_by_abbr(params.body_material))
        back_panel = params.width * \
                    (params.height + 0.015) * \
                    (MaterialBase.get_price_by_abbr(params.backplate_material))
        bath = params.width * \
               0.300 * \
              (MaterialBase.get_price_by_abbr(params.body_material))
    else:
        side_panel = 2 * ((params.depth / 2 + 0.015) * \
                     (params.height + 0.045) * \
                     (MaterialBase.get_price_by_abbr(params.body_material)))
        top_panel = params.width * \
                    (params.depth + 0.250) * \
                    (MaterialBase.get_price_by_abbr(params.body_material))
        back_panel = params.width * \
                    (params.height + 0.015) * \
                    (MaterialBase.get_price_by_abbr(params.backplate_material))
        bath = params.width * \
              0.300 * \
             (MaterialBase.get_price_by_abbr(params.body_material))
    branch_pipe = 0.8 * 0.075 * MaterialBase.get_price_by_abbr(params.backplate_material)
    faucet = (1 if params.width <= 1.100 else 2) * MaterialBase.get_price_by_id(124)
    total_cost = 2 * side_panel + top_panel + bath + (back_panel if not Series.is_island else 0) + branch_pipe + faucet
    print(side_panel, 'side panel')
    print(top_panel, 'top panel')
    print(back_panel, 'back panel')
    print(bath, 'bath')
    print(branch_pipe, 'branch_pipe')
    print(faucet, 'faucet')
    print(total_cost, 'total body')
        
    return total_cost


FORMULA_HANDLERS: dict[
    tuple[bool, ZVNFormula],
    Callable[[ZVNSeries, MaterialCollector, ZVNParams | ZPVNParams], float],
] = {
    (False, ZVNFormula.FORMULA_01_02): calculate_01_02,
    (False, ZVNFormula.FORMULA_03_05): calculate_03_05,
    (True, ZVNFormula.FORMULA_01_02): calculate_01_02,
    (True, ZVNFormula.FORMULA_03_05): calculate_03_05,
}


def handle_body_calculation(
        Series: ZVNSeries, 
        MaterialBase: MaterialCollector,
        params: ZVNParams | ZPVNParams) -> float:
    calculation_route = detect_calculation_route(Series)
    handler = FORMULA_HANDLERS.get(calculation_route)

    if handler is None:
        raise ValueError(f"No handler found for calculation route {calculation_route}")
    
    base_cost = handler(Series, MaterialBase, params)
    return base_cost


def calculate_production_cost(
        Series: ZVNSeries,
        MaterialBase: MaterialCollector,
        params: ZVNParams | ZPVNParams) -> float:
    total_cost = 0
    
    
    
    # подвес
    bracket = (0.17 * 0.08) * MaterialBase.get_price_by_id(1) # 1 - id нержавейки aisi 430 0.8мм
    # Рассекатели (ставятся по 1 на каждый 400мм)
    if Series.has_supply: 
        dividers = (
            (
                (0.035*0.57) * 3 + 
                (0.15*0.055) * 2 + 
                (0.58*0.055) * 2) * 
                MaterialBase.get_price_by_abbr(params.body_material) + 100
            ) * (2 if Series.is_island else 1)
    else:
        dividers = 0

    dividers *= (params.depth + 0.39) // 0.4
    components = MaterialBase.calculate_misc()
    work_price = MaterialBase.get_price_by_abbr('работа.' + Series._value_)
    filters_cost = calculate_filters_cost(Series, MaterialBase, params)

    ind_features = 0

    # расчет полок и притоков
    if Series.model == '01':
        if Series.has_supply:
            ind_features += (params.width) * 0.2 * MaterialBase.get_price_by_abbr(params.body_material)
    elif Series.model == '02':
        if Series.has_supply:
            ind_features += (
                params.width * (params.height + 0.3) *
                MaterialBase.get_price_by_abbr(params.body_material)
            )
    else:
        if Series.has_supply:
            ind_features += (
                # Полка
                params.width * 0.17 * MaterialBase.get_price_by_abbr(params.body_material) + \
                # Приток
                params.width * (params.height + 0.3) * MaterialBase.get_price_by_abbr(params.body_material)
            )
        else:
            ind_features += params.width * 0.17 * MaterialBase.get_price_by_abbr(params.body_material)
                
    total_cost = (4 * bracket) + dividers + components + work_price + ind_features + filters_cost
    print(bracket, 'bracket')
    print(dividers, 'dividers')
    print(components, 'components')
    print(work_price, 'work price')
    print(ind_features, 'ind features')
    print(filters_cost, 'filter cost')

    print(total_cost)
    return total_cost


def parse_lights(lights: str) -> tuple[str, int]:
    if not lights:
        return '', 0

    lights_abbr, _, lights_count_raw = lights.partition('(')
    lights_abbr = lights_abbr.strip()

    if not lights_count_raw:
        return lights_abbr, 1

    count_match = re.search(r'\d+', lights_count_raw)
    lights_count = int(count_match.group()) if count_match else 1

    return lights_abbr, lights_count


def calculate_additional_cost(
        Series: ZVNSeries,
        MaterialBase: MaterialCollector,
        params: ZVNParams | ZPVNParams) -> float:
    lights_abbr, lights_count = parse_lights(params.lights)
    light_cost = MaterialBase.get_price_by_abbr(lights_abbr) * lights_count if lights_abbr else 0
    cut_out_cost = 0
    if Series.has_supply:
        # + 2 параметра на врезки
        cut_out_cost += MaterialBase.get_price_by_abbr(params.main_cut_in)
        cut_out_cost += MaterialBase.get_price_by_abbr(params.add_cut_in)

    cut_out_cost += MaterialBase.get_price_by_abbr(params.main_cut_out)
    cut_out_cost += MaterialBase.get_price_by_abbr(params.add_cut_out)

    fan_cost = MaterialBase.get_price_by_abbr(params.fan)

    total_cost = light_cost + cut_out_cost + fan_cost
    print(light_cost, 'light cost')
    print(cut_out_cost, ' cut out cost')
    print(fan_cost, 'fan cost')
    print(total_cost)
    return total_cost


def get_marginality(MaterialBase: MaterialCollector):
    return MaterialBase.get_price_by_abbr('наценка')
