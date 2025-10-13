from enum import Enum


class ShelfType(Enum):
    STANDART = ('С', 'спл')
    PERFORATED = ('П', 'пер')
    GRILLE = ('Р', 'реш')

    def __new__(cls, description: str, abbr: str):
        obj = object.__new__(cls)
        obj._value_ = description
        obj.abbr = abbr
        return obj


    @classmethod
    def get_type(cls, value: str) -> 'ShelfType':
        """
        Возвращает тип полки по аббревиатуре или названию.
        Если значение не найдено, возвращает cls.STANDART.
        """
        # Создаем словарь, где ключами являются как аббревиатуры, так и названия
        type_map = {item.abbr: item for item in cls}
        type_map.update({item.value: item for item in cls})
        return type_map.get(value, cls.STANDART)
