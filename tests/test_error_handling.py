import asyncio

import pytest
from fastapi import HTTPException

from app.data.material_collector import MaterialCollector
from app.main import calc_controller, calculate_cost, repository
from app.schemas import CalculationRequest


def test_calculate_preserves_http_exception_status(monkeypatch) -> None:
    async def fail_calculation(series: str, parameters: str):
        raise HTTPException(status_code=400, detail="bad calculation input")

    monkeypatch.setattr(repository, "get_calculated_product_cost", lambda *_: None)
    monkeypatch.setattr(calc_controller, "calculation", fail_calculation)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(calculate_cost(CalculationRequest(series="TEST", parameters="1/2/3")))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "bad calculation input"


def test_material_collector_get_price_by_id_reports_missing_material() -> None:
    collector = MaterialCollector.__new__(MaterialCollector)
    collector.series = "Стеллаж СтПП"
    collector.materials = {}

    with pytest.raises(KeyError, match="Material id 12 not found"):
        collector.get_price_by_id(12)


def test_material_collector_supports_legacy_get() -> None:
    collector = MaterialCollector.__new__(MaterialCollector)
    collector.materials = {12: ["abbr", "name", False, 100.0]}

    assert collector.get(12) == ["abbr", "name", False, 100.0]
    assert collector.get(999, ["default"]) == ["default"]
