from enum import Enum


class GussetType(Enum):
    STANDART = ('С', 'стандарт', '-')
    LASER_CUT = ('Л', 'лазерная резка', 'рез.лазер')
    CARVED = ('Р', 'резная форма', 'рез.форма')

    def __new__(cls, short: str, description: str, abbr: str):
        obj = object.__new__(cls)
        obj._value_ = short
        obj.description = description
        obj.abbr = abbr
        return obj

    @classmethod
    def get_type(cls, value: str) -> 'GussetType':
        """
        Возвращает тип полки по аббревиатуре или названию.
        Если значение не найдено, возвращает cls.STANDART.
        """
        type_map = {}
        for item in cls:
            type_map[item.value] = item
            type_map[item.abbr] = item
            type_map[item.description] = item
        return type_map.get(value, cls.STANDART)
