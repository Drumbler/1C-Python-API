import re
from typing import Callable

from app.data.dto.zvn_dto import ZPVNParams, ZVNParams
from app.data.material_collector import MaterialCollector
from app.utils.custom.ZVNformula_class import ZVNFormula
from app.utils.custom.ZVNseries_class import ZVNSeries


def detect_formula(Series: ZVNSeries):
    return Series.formula


def calculate_01_02(
        Series: ZVNSeries, 
        MaterialBase: MaterialCollector, 
        params: ZVNParams | ZPVNParams) -> float:
    
    back_panel = 0
    if not Series.has_supply:
        side_panel = (params.depth + 0.015) * \
                     (params.height + 0.035) * \
                     MaterialBase.get_price_by_abbr(params.body_material)
        top_panel = (params.width) * \
                    (params.depth + (0.165 if Series.model == '01' else 0.135)) * \
                    MaterialBase.get_price_by_abbr(params.body_material)
        back_panel = (params.width) * \
                     (params.height + 0.015) * \
                     MaterialBase.get_price_by_abbr(params.backplate_material)
        bath = params.width * 0.3 * \
               MaterialBase.get_price_by_abbr(params.body_material)
    else:
        side_panel = 2 * ((params.depth / 2) + 0.015) * \
                     (params.height + 0.035) * \
                     MaterialBase.get_price_by_abbr(params.body_material)
        top_panel = (params.width) * \
                    (params.depth + (0.165 if Series.model == '01' else 0.135)) * \
                    MaterialBase.get_price_by_abbr(params.body_material)
        # back_panel = (params.width) * \
        #              (params.height + 0.015) * \
        #              MaterialBase.get_price_by_abbr(params.backplate_material)
        bath = params.width * 0.3 * \
               MaterialBase.get_price_by_abbr(params.body_material)
    
    total_cost = 2 * side_panel + top_panel + \
                 back_panel + bath
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
        # back_panel = params.width * \
        #             (params.height + 0.015) * \
        #             (MaterialBase.get_price_by_abbr(params.backplate_material))
        bath = params.width * \
               0.300 * \
              (MaterialBase.get_price_by_abbr(params.body_material))
        
    total_cost = 2 * side_panel + top_panel + bath + (back_panel if Series.is_island else 0)
        
    return total_cost


FORMULA_HANDLERS: dict[
    ZVNFormula,
    Callable[[ZVNSeries, MaterialCollector, ZVNParams | ZPVNParams], float],
] = {
    ZVNFormula.FORMULA_01_02: calculate_01_02,
    ZVNFormula.FORMULA_03_05: calculate_03_05,
}


def handle_body_calculation(
        Series: ZVNSeries, 
        MaterialBase: MaterialCollector,
        params: ZVNParams | ZPVNParams) -> float:
    formula = detect_formula(Series)
    handler = FORMULA_HANDLERS.get(formula)

    if handler is None:
        raise ValueError(f"No handler found for formula {formula}")
    
    base_cost = handler(Series, MaterialBase, params)
    return base_cost


def calculate_production_cost(
        Series: ZVNSeries,
        MaterialBase: MaterialCollector,
        params: ZVNParams | ZPVNParams) -> float:
    total_cost = 0
    
    branch_pipe = 0.8 * 0.075 * MaterialBase.get_price_by_abbr(params.backplate_material)
    faucet = (1 if params.width <= 1.100 else 2) * MaterialBase.get_price_by_id(124)
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

    ind_features = 0

    # расчет полок и притоков
    if Series.model == '01':
        if Series.has_supply:
            ind_features += (params.width) * 0.2 * MaterialBase.get_price_by_abbr(params.body_material)
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
                
    total_cost = branch_pipe + faucet + bracket + dividers + components + work_price + ind_features
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

    filters_cost = MaterialBase.get_price_by_abbr(params.filters)

    fan_cost = MaterialBase.get_price_by_abbr(params.fan)

    total_cost = light_cost + cut_out_cost + filters_cost + fan_cost
    return total_cost


def get_marginality(MaterialBase: MaterialCollector):
    return MaterialBase.get_price_by_abbr('наценка')
