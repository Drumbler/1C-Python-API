from dataclasses import dataclass

from app.data.dto.base_dto import BaseParams
from app.utils.custom.shelf_class import ShelfType


@dataclass(slots=True)
class VMXParams(BaseParams):
    series_letter: str
    number_of_baths: int
    height_bath: float
    width_bath: float
    depth_bath: float
    needed_color: str | None
    board_size: float
    number_of_tap_hole: int
    type_of_tap_hole: str | None
    type_of_drain_hole: str | None
    need_onepiece_bath: bool
    abbr_onepiece_bath: str | None
    welded: bool
    wheels: str | None
    apron: str | None
    shelf_material: str | None
    shelf_type: ShelfType | None
    shelf_is_strapping_3sides: bool
