from decimal import Decimal, ROUND_HALF_UP
import re

CALCULATED_PRODUCTS_TABLE = 'calculated_products'
CALCULATED_PRODUCTS_ZVN_TEMPLATE = (
    'н.ст.08',
    'задн.ст.ОЦИНК',
    'не.краш',
    'врез.выт',
    '-',
    'без.подсв',
    'вент.нет',
    'сборн',
)
CALCULATED_PRODUCTS_ZPVN_TEMPLATE = (
    'н.ст.08',
    'задн.ст.ОЦИНК',
    'не.краш',
    'врез.выт',
    '-',
    'врез.прит',
    '-',
    'без.подсв',
    'вент.нет',
    'сборн',
)
STANDARD_FILTER_NAME = 'ст.фильтры'
PREMIUM_FILTER_NAME = 'премиум.жир'
PREMIUM_BACKPLATE_NAME = 'задн.ст.НЕРЖ'
PREMIUM_SERIES_MARKER = 'ПРЕМИУМ'

CHARACTERISTIC_PATTERN = re.compile(r'^\s*(\d+)\s*[xх*]\s*(\d+)\s*[xх*]\s*(\d+)\s*$')


def round_calculated_product_cost(cost: float | int) -> int:
    return int(Decimal(str(cost)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def normalize_calculated_product_series(series: str) -> str:
    return ' '.join(series.strip().split()).upper()


def normalize_calculated_product_parameters(parameters: str) -> str:
    normalized_parts = [part.strip() for part in parameters.split('/')]

    while normalized_parts and not normalized_parts[0]:
        normalized_parts.pop(0)
    while normalized_parts and not normalized_parts[-1]:
        normalized_parts.pop()

    return '/'.join(normalized_parts)


def build_calculated_product_parameters(series: str, characteristic: str) -> str:
    normalized_series = normalize_calculated_product_series(series)
    match = CHARACTERISTIC_PATTERN.match(characteristic)
    if match is None:
        raise ValueError(f'Unsupported characteristic format: {characteristic!r}')

    width, depth, height = match.groups()
    filter_name = (
        PREMIUM_FILTER_NAME
        if PREMIUM_SERIES_MARKER in normalized_series
        else STANDARD_FILTER_NAME
    )
    backplate_name = (
        PREMIUM_BACKPLATE_NAME
        if PREMIUM_SERIES_MARKER in normalized_series
        else CALCULATED_PRODUCTS_ZVN_TEMPLATE[1]
    )
    is_island = re.search(r'-04/0\d', normalized_series) is not None

    if normalized_series.startswith('ЗПВН'):
        parts = [
            width,
            depth,
            height,
            CALCULATED_PRODUCTS_ZPVN_TEMPLATE[0],
            *(() if is_island else (backplate_name,)),
            CALCULATED_PRODUCTS_ZPVN_TEMPLATE[2],
            filter_name,
            *CALCULATED_PRODUCTS_ZPVN_TEMPLATE[3:],
        ]
    elif normalized_series.startswith('ЗВН'):
        parts = [
            width,
            depth,
            height,
            CALCULATED_PRODUCTS_ZVN_TEMPLATE[0],
            *(() if is_island else (backplate_name,)),
            CALCULATED_PRODUCTS_ZVN_TEMPLATE[2],
            filter_name,
            *CALCULATED_PRODUCTS_ZVN_TEMPLATE[3:],
        ]
    else:
        raise ValueError(f'Unsupported zont series: {series!r}')

    return '/'.join(parts)


def prepare_calculated_product_parameters(series: str, characteristic: str) -> str:
    normalized_characteristic = normalize_calculated_product_parameters(characteristic)
    if CHARACTERISTIC_PATTERN.match(normalized_characteristic):
        return build_calculated_product_parameters(series, normalized_characteristic)

    normalized_series = normalize_calculated_product_series(series)
    parts = normalized_characteristic.split('/')
    if (
        normalized_series.startswith(('ВМ', 'ВК'))
        and len(parts) >= 4
        and all(part.isdigit() for part in parts[:3])
    ):
        return normalized_characteristic

    raise ValueError(
        f'Unsupported characteristic for series {series!r}: {characteristic!r}'
    )
