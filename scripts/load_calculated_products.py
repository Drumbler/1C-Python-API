import argparse
import sys
from pathlib import Path


from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT_DIR / "Товары из прайса в базу.xlsx"
load_dotenv(ROOT_DIR / ".env")
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.data.DBrepository import DBrepository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load calculated product prices from an Excel workbook."
    )
    parser.add_argument("source", nargs="?", type=Path, default=SOURCE_PATH)
    return parser.parse_args()

from app.data.database_pool import pool


def main() -> None:
    args = parse_args()
    repository = DBrepository(pool)
    loaded_rows = repository.load_calculated_products_from_xlsx(args.source)
    print(f"Loaded rows into calculated_products: {loaded_rows}")


if __name__ == "__main__":
    main()
