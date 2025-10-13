# from app.data.classes import ShelfType

# parsed_params = {'shelf_count': '-', 'shelf_type': 'STANDART'}

# shelf_count = parsed_params.get('shelf_count')
# shelf_count = (int(shelf_count.split(
#     'шт')[0])) if shelf_count != '-' else 0
# print(shelf_count)
# print(type(shelf_count))
from re import findall


def find_series_last_char(series: str) -> str:

    TARGET_LETTERS = 'БНЛПЭСУ'
    matches = findall(r"[{}]".format(TARGET_LETTERS), series)
    return matches[-1] if matches else None

print(find_series_last_char('Стеллаж СтПЭ'))