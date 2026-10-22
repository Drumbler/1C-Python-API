import pytest

from app.controllers.module_loader import CalculationModuleRegistry


@pytest.fixture(scope="module")
def registry() -> CalculationModuleRegistry:
    registry = CalculationModuleRegistry()
    registry.discover()
    return registry


def test_registry_discovers_calculators_and_normalizes_legacy_paths(
    registry: CalculationModuleRegistry,
) -> None:
    count = len(registry.registered_keys())

    assert count >= 1
    canonical_module = registry.get("zonts.zvn")
    assert registry.get("zonts/zvn.py") is canonical_module
    assert registry.get("app.modules.zonts.zvn") is canonical_module
    assert registry.get("zvn.py") is canonical_module


def test_registry_rejects_unknown_module(
    registry: CalculationModuleRegistry,
) -> None:
    with pytest.raises(ImportError, match="not found"):
        registry.get("missing.module")
