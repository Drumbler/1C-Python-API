import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT_DIR / "Товары из прайса в базу.xlsx"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.data.DBrepository import DBRepository


def main() -> None:
    repository = DBRepository()
    loaded_rows = repository.load_calculated_products_from_xlsx(SOURCE_PATH)
    print(f"Loaded rows into calculated_products: {loaded_rows}")


if __name__ == "__main__":
    main()
