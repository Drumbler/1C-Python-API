from enum import Enum


class ShelfType(Enum):
    STANDART = ('С', 'спл', 'спл.полка')
    PERFORATED = ('П', 'пер', 'пер.полка')
    GRILLE = ('Р', 'реш', 'полка-решетка')

    def __new__(cls, short: str, description: str, abbr: str):
        obj = object.__new__(cls)
        obj._value_ = short
        obj.description = description
        obj.abbr = abbr
        return obj

    @classmethod
    def get_type(cls, value: str) -> 'ShelfType':
        """
        Возвращает тип полки по аббревиатуре или названию.
        Если значение не найдено, возвращает cls.STANDART.
        """
        # Создаем словарь, где ключами являются как аббревиатуры, так и названия
        type_map = {}
        for item in cls:
            type_map[item.value] = item
            type_map[item.abbr] = item
            type_map[item.description] = item
        return type_map.get(value, cls.STANDART)
