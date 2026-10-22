import importlib
import pkgutil
from collections import defaultdict
from logging import getLogger
from types import ModuleType

logger = getLogger(__name__)


class CalculationModuleRegistry:
    """Process-local registry of product calculation modules."""

    def __init__(self, package_name: str = "app.modules") -> None:
        self.package_name = package_name
        self._modules: dict[str, ModuleType] = {}
        self._canonical_keys: set[str] = set()
        self._import_errors: dict[str, str] = {}

    @staticmethod
    def _normalize_key(module_path: str) -> str:
        if not isinstance(module_path, str) or not module_path.strip():
            raise ValueError("Calculation module path cannot be empty")

        key = module_path.strip().replace("\\", "/")
        lowered_key = key.casefold()
        for suffix in (".pyc", ".py"):
            if lowered_key.endswith(suffix):
                key = key[:-len(suffix)]
                break

        key = key.replace("/", ".").strip(".")
        lowered_key = key.casefold()
        for prefix in ("app.modules.", "modules."):
            if lowered_key.startswith(prefix):
                key = key[len(prefix):]
                break

        return key.strip(".").casefold()

    def discover(self) -> int:
        """Import calculator modules and atomically replace the registry."""
        package = importlib.import_module(self.package_name)
        discovered: dict[str, ModuleType] = {}
        short_names: dict[str, list[tuple[str, ModuleType]]] = defaultdict(list)
        import_errors: dict[str, str] = {}

        prefix = f"{package.__name__}."
        for module_info in pkgutil.walk_packages(package.__path__, prefix=prefix):
            module_name = module_info.name
            if module_info.ispkg or self._is_excluded(module_name):
                continue

            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                relative_name = module_name.removeprefix(prefix)
                import_errors[self._normalize_key(relative_name)] = str(exc)
                continue

            if not self._is_calculator(module):
                continue

            relative_name = module_name.removeprefix(prefix)
            canonical_key = self._normalize_key(relative_name)
            if canonical_key in discovered:
                raise RuntimeError(
                    f"Duplicate calculation module key: {relative_name}"
                )

            discovered[canonical_key] = module
            short_names[canonical_key.rsplit(".", 1)[-1]].append(
                (canonical_key, module)
            )

        if not discovered:
            details = "; ".join(
                f"{key}: {error}" for key, error in import_errors.items()
            )
            raise RuntimeError(
                f"No calculation modules found in package {self.package_name}. "
                f"Import errors: {details}"
            )

        for module_key, error in import_errors.items():
            logger.warning(
                "Calculation module %s was skipped because it cannot be imported: %s",
                module_key,
                error,
            )

        canonical_keys = set(discovered)
        for short_name, candidates in short_names.items():
            if len(candidates) != 1:
                logger.warning(
                    "Short calculation module name %r is ambiguous: %s",
                    short_name,
                    ", ".join(key for key, _ in candidates),
                )
                continue

            canonical_key, module = candidates[0]
            existing = discovered.get(short_name)
            if existing is None or existing is module:
                discovered[short_name] = module
            else:
                logger.warning(
                    "Short calculation module name %r conflicts with %r",
                    short_name,
                    canonical_key,
                )

        # Replace only after discovery succeeds so requests cannot observe a
        # partially populated registry.
        self._modules = discovered
        self._canonical_keys = canonical_keys
        self._import_errors = import_errors
        logger.info(
            "Loaded %d calculation modules: %s",
            len(canonical_keys),
            ", ".join(sorted(canonical_keys)),
        )
        return len(canonical_keys)

    def get(self, module_path: str) -> ModuleType:
        if not self._modules:
            raise RuntimeError("Calculation module registry is not initialized")

        key = self._normalize_key(module_path)
        if key in self._import_errors:
            raise ImportError(
                f"module {module_path} could not be loaded: "
                f"{self._import_errors[key]}"
            )
        try:
            return self._modules[key]
        except KeyError as exc:
            raise ImportError(
                f"module {module_path} not found (Модуль не найден)"
            ) from exc

    def registered_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._canonical_keys))

    @staticmethod
    def _is_calculator(module: ModuleType) -> bool:
        return callable(getattr(module, "calculate", None)) or callable(
            getattr(module, "calculate_details", None)
        )

    @staticmethod
    def _is_excluded(module_name: str) -> bool:
        # Component calculators update material prices and are loaded separately.
        return module_name.startswith("app.modules.components.")


calculation_module_registry = CalculationModuleRegistry()


def load_module_by_path(file_location: str) -> ModuleType:
    """Return an already imported calculator from the process registry."""
    return calculation_module_registry.get(file_location)


def load_all_modules() -> dict[str, ModuleType]:
    """Load component calculators from source or sourceless bytecode packages."""
    components_package = importlib.import_module("app.modules.components")
    modules: dict[str, ModuleType] = {}

    for module_info in pkgutil.iter_modules(components_package.__path__):
        module_name = module_info.name
        if module_name.startswith("_"):
            continue

        try:
            module = importlib.import_module(
                f"{components_package.__name__}.{module_name}"
            )
            modules[module_name] = module
        except Exception as exc:
            logger.warning("Error loading module %s: %s", module_name, exc)

    return modules
