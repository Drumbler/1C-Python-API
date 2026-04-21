from dataclasses import dataclass

from app.data.dto.base_dto import BaseParams


@dataclass(slots=True)
class ZVNParams(BaseParams):
    body_material: str
    backplate_material: str
    ral: str
    filters: str
    main_cut_out: str
    add_cut_out: str
    lights: str
    fan: str
    weld: str
    is_cube: bool
    is_premium: bool


@dataclass(slots=True)
class ZPVNParams(BaseParams):
    body_material: str
    backplate_material: str
    ral: str
    filters: str
    main_cut_out: str
    add_cut_out: str
    main_cut_in: str
    add_cut_in: str
    lights: str
    fan: str
    weld: str
    is_cube: bool
    is_premium: bool
