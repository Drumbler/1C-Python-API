import pytest

from app.modules.baths import new_vmx
from app.modules.shelvings import new_stpx
from app.modules.shelvings_handler import calculate_shelfs_cost
from app.utils.custom.shelf_class import ShelfType
from app.utils.custom.shelvings_class import ShelvingSeries


class FakeMaterialCollector:
    def __init__(self, series: str = ""):
        self.series = series
        self.by_id = {
            12: 2.0,
            17: 10.0,
            225: 5.0,
            226: 0.2,
        }
        self.by_abbr = {
            "-": 0.0,
            "н.ст.08": 100.0,
            "430.н.ст.10": 200.0,
            "Н.стойк": 10.0,
            "Н.обв": 20.0,
            "н.ст.15": 30.0,
            "оц.ст.08": 40.0,
            "работа.ВМН-1": 50.0,
            "наценка.ВМН-1": 0.2,
            "сварн.": 50.0,
            "опора": 7.0,
        }

    def calculate_misc(self) -> float:
        return 11.0 if self.series == "Стеллаж СтПП" else 5.0

    def get_price_by_id(self, material_id: int) -> float:
        return self.by_id[material_id]

    def get_price_by_abbr(self, material_abbr: str) -> float:
        return self.by_abbr.get(material_abbr, 0.0)


def test_new_stpx_cost_calculation_uses_fake_material_prices(monkeypatch) -> None:
    monkeypatch.setattr(new_stpx, "MaterialCollector", FakeMaterialCollector)
    params = new_stpx.parse_parameters(
        "1000/600/1800/-/н.ст.08/-/1/С/усиление.нет/сварн./опора",
        "Стеллаж СтПП",
    )

    total_cost, markup = new_stpx.cost_calculation(params, ShelvingSeries.STPP)

    assert markup == pytest.approx(1.15)
    assert total_cost == pytest.approx(249.9985)


def test_shelving_shelf_formula_applies_perforated_markup() -> None:
    params = new_stpx.parse_parameters(
        "1000/600/1800/-/н.ст.08/-/1/П/усиление.нет/-/-",
        "Стеллаж СтПП",
    )

    assert calculate_shelfs_cost(FakeMaterialCollector("Стеллаж СтПП"), params) == pytest.approx(
        92.432
    )


def test_new_vmx_cost_calculation_uses_fake_material_prices(monkeypatch) -> None:
    import app.data.material_collector as material_collector

    monkeypatch.setattr(material_collector, "MaterialCollector", FakeMaterialCollector)
    params = new_vmx.parse_parameters("1000/600/850/глуб.м.о.300", "ВМН-1")

    total_cost, markup = new_vmx.cost_calculation(params, "ВМН-1")

    assert markup == pytest.approx(1.3)
    assert total_cost == pytest.approx(655.0804)
