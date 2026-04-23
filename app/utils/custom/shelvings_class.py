
from enum import Enum


class ShelvingSeries(Enum):
    STPB = ('Стеллаж СтПБ', 'СтПБ', 11)
    STPL = ('Стеллаж СтПЛ', 'СтПЛ', 10)
    STPN = ('Стеллаж СтПН', 'СтПН', 9)
    STPU = ('Стеллаж СтПУ', 'СтПУ',  356)
    STPE = ('Стеллаж СтПЭ', 'СтПЭ', 19)
    STPER = ('Стеллаж СтПЭр', 'СтПЭр', 20)
    STPP = ('Стеллаж СтПП', 'СтПП', 17)
    STPPR = ('Стеллаж СтППр', 'СтППр', 18)
    STPS = ('Стеллаж СтПС', 'СтПС', 354)
    STPSR = ('Стеллаж СтПСр', 'СтПСр', 353)

    def __new__(cls, code: str, model: str, material: int):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.model = model
        obj.material = material
        return obj
