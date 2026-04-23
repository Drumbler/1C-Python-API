from enum import Enum

from app.utils.custom.ZVNformula_class import ZVNFormula


class ZVNSeries(Enum):
    ZVN01 = ('ЗВН-01', ZVNFormula.FORMULA_01_02, '01', False, False)
    ZVN02 = ('ЗВН-02', ZVNFormula.FORMULA_01_02, '02', False, False)
    ZVN03 = ('ЗВН-03', ZVNFormula.FORMULA_03_05, '03', False, False)
    ZVN05 = ('ЗВН-05', ZVNFormula.FORMULA_03_05, '05', False, False)
    ZPVN01 = ('ЗПВН-01', ZVNFormula.FORMULA_01_02, '01', False, True)
    ZPVN02 = ('ЗПВН-02', ZVNFormula.FORMULA_01_02, '02', False, True)
    ZPVN03 = ('ЗПВН-03', ZVNFormula.FORMULA_03_05, '03', False, True)
    ZPVN05 = ('ЗПВН-05', ZVNFormula.FORMULA_03_05, '05', False, True)
    ZVN0401 = ('ЗВН-04/01', ZVNFormula.FORMULA_01_02, '01', True, False)
    ZVN0402 = ('ЗВН-04/02', ZVNFormula.FORMULA_01_02, '02', True, False)
    ZVN0403 = ('ЗВН-04/03', ZVNFormula.FORMULA_03_05, '03', True, False)
    ZVN0405 = ('ЗВН-04/05', ZVNFormula.FORMULA_03_05, '05', True, False)
    ZPVN0401 = ('ЗПВН-04/01', ZVNFormula.FORMULA_01_02, '01', True, True)
    ZPVN0402 = ('ЗПВН-04/02', ZVNFormula.FORMULA_01_02, '02', True, True)
    ZPVN0403 = ('ЗПВН-04/03', ZVNFormula.FORMULA_03_05, '03', True, True)
    ZPVN0405 = ('ЗПВН-04/05', ZVNFormula.FORMULA_03_05, '05', True, True)

    def __new__(cls,
                code: str,
                formula: ZVNFormula,
                model: str,
                is_island: bool,
                has_supply: bool,
                ):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.formula = formula
        obj.model = model
        obj.is_island = is_island
        obj.has_supply = has_supply
        return obj
        
