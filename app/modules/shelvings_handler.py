from __future__ import annotations

from typing import TYPE_CHECKING

from app.data.dto.shelvings_dto import ProductionShelvingsParams
from app.utils.custom.shelf_class import ShelfType
from app.utils.custom.shelvings_class import ShelvingSeries

if TYPE_CHECKING:
    from app.data.material_collector import MaterialCollector


EASY_WIDTHS = frozenset({
    0.6, 0.7, 0.8, 1.16,
})
EASY_DEPTHS = frozenset({
    0.3, 0.4, 0.5, 0.6, 0.7,
})
EASY_MATERIALS = frozenset({'н.ст.08'})

EXTRA_REINFORCEMENT = 'усиление.да'
DISASSEMBLED_WELD = 'разборн.'
ASSEMBLY_ABBR = 'сборн.'
DEFAULT_RAL = '-'
DEFAULT_SHELF_MATERIAL = 'н.ст.08'


def parse_shelving_series(series: str) -> ShelvingSeries:
    normalized_series = series.strip().casefold()
    for item in ShelvingSeries:
        if normalized_series in {item.value.casefold(), item.model.casefold()}:
            return item

    raise ValueError(f"Unsupported shelving series: {series!r}")


def normalize_weld_option(weld: str) -> str:
    if weld == DISASSEMBLED_WELD:
        return ASSEMBLY_ABBR
    return weld


def calculate_shelf_reinforcement(
    MaterialBase: MaterialCollector,
    params: ProductionShelvingsParams,
) -> float:
    return (params.width + 0.09) * MaterialBase.get_price_by_id(12)


def calculate_shelf_cost(
    MaterialBase: MaterialCollector,
    params: ProductionShelvingsParams,
    shelf_type: ShelfType | None,
) -> float:
    shelf_material = params.shelf_material or DEFAULT_SHELF_MATERIAL
    ral_shelfs = params.ral_shelfs or DEFAULT_RAL
    shelf_type = shelf_type or ShelfType.STANDART

    shelf_area = (params.width + 0.09) * (params.depth + 0.09)
    shelf_cost = shelf_area * MaterialBase.get_price_by_abbr(shelf_material)
    ral_cost = shelf_area * MaterialBase.get_price_by_abbr(ral_shelfs)

    match shelf_type:
        case ShelfType.PERFORATED:
            shelf_cost *= 1 + MaterialBase.get_price_by_id(226)
        case ShelfType.GRILLE:
            shelf_cost += MaterialBase.get_price_by_id(225)

    return shelf_cost + ral_cost + calculate_shelf_reinforcement(MaterialBase, params)


def calculate_shelfs_cost(
    MaterialBase: MaterialCollector,
    params: ProductionShelvingsParams,
) -> float:
    if len(params.shelfs_order) != params.shelfs_number:
        raise ValueError(
            "Shelfs order length must match shelfs number: "
            f"{len(params.shelfs_order)} != {params.shelfs_number}"
        )

    shelfs_cost = 0.0
    has_extra_reinforcement = params.additional_reinforcement == EXTRA_REINFORCEMENT
    for shelf_type in params.shelfs_order:
        normalized_shelf_type = (
            shelf_type
            if isinstance(shelf_type, ShelfType)
            else ShelfType.get_type(shelf_type)
        )
        shelfs_cost += calculate_shelf_cost(MaterialBase, params, normalized_shelf_type)
        if has_extra_reinforcement:
            shelfs_cost += calculate_shelf_reinforcement(MaterialBase, params)

    return shelfs_cost


def calculate_pillars_cost(
    series: ShelvingSeries,
    MaterialBase: MaterialCollector,
    params: ProductionShelvingsParams,
) -> float:
    ral_pillars = params.ral_pillars or DEFAULT_RAL
    pillar_count = 4 if params.width <= 1.800 else 6

    pillar_cost = params.height * MaterialBase.get_price_by_id(series.material)
    ral_cost = 0.04 * 2 * params.height * MaterialBase.get_price_by_abbr(ral_pillars)

    return (pillar_cost + ral_cost) * pillar_count


def calculate_options_cost(
    MaterialBase: MaterialCollector,
    params: ProductionShelvingsParams,
) -> float:
    weld_abbr = normalize_weld_option(params.weld)
    return (
        MaterialBase.get_price_by_abbr(weld_abbr)
        + MaterialBase.get_price_by_abbr(params.stands)
    )


def calculate_difficulty_coef(params: ProductionShelvingsParams) -> float:
    criteria = (
        (params.width, EASY_WIDTHS, 0.05),
        (params.depth, EASY_DEPTHS, 0.05),
        (params.shelf_material, EASY_MATERIALS, 0.10),
    )

    coef = 0.0
    for value, allowed, weight in criteria:
        if params.width == 1.16 and allowed in (EASY_WIDTHS, EASY_MATERIALS):
            continue
        if value in allowed:
            coef += weight

    return 1 + coef
