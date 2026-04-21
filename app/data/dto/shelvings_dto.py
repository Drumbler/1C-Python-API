from dataclasses import dataclass

from app.data.dto.base_dto import BaseParams
from app.utils.custom.shelf_class import ShelfType


@dataclass(slots=True)
class ProductionShelvingsParams(BaseParams):
    ral_pillars: str
    shelf_material: str
    ral_shelfs: str
    shelfs_number: int
    shelfs_order: list[ShelfType]
    additional_reinforcement: str
    weld: str
    stands: str




