import re
from typing import Dict, List
from app.data.DBrepository import DBRepository


dbrepo = DBRepository()


class MaterialCollector:
    '''
    Класс для подбора материалов для изделия из базы данных.
    '''
    def __init__(self, series):
        self.series = series
        self.materials: Dict = dbrepo.get_materials_for_products(self.series)

    def calculate_misc(self) -> float:
        '''
        Метод расчета стоимости комплекта поставки и прочих допов для изделий
        Помимо расчета удаляет из self.materials лишние записи, которые уже были использованы
        '''
        misc = 0
        keys_to_drop = []
        misc_ind = 2
        for key, lst in self.materials.items(): 
            if len(lst) > misc_ind and lst[misc_ind]:
                misc += lst[-1]
                keys_to_drop.append(key)
        

        for key in keys_to_drop:
            del self.materials[key]
        return float(misc)

    def collect_materials(self, unknown_materials: List = None):
        '''
        Может понадобиться в будущем, на данный момент функция не используется!!!
        Добавляет в self.materials материалы из списка(по аббревиатуре) по запросу
        '''
        new_entries = dbrepo.get_parameters_for_db(
            unknown_materials, 'abberviation',
            list_of_column_names=['id', 'abbreviation', 'name', 'misc', 'price'])
        self.materials.update(new_entries)

    def get_price_by_abbr(self, material_abbr: str) -> float:
        '''
        Метод для получения цены материала по аббревиатуре из self.materials, до этого в self.materials 
        загружается выгрузка базы материалов.
        врез.выт, врез.доп.выт, врез.прит, врез.доп.прит
        '''
        abbr_ind = 0
        for _, lst in self.materials.items():
            if len(lst) > abbr_ind and material_abbr in lst[abbr_ind]:
                return lst[-1]
        print(f'Материал {material_abbr} не найден в базе данных. Возможно он отсутствует в таблице "materials_for_products"')
        return 0

    def get_price_by_id(self, material_id: int) -> float:
        '''
        Метод для получения цены материала по id из self.materials, до этого в self.materials
        загружается выгрузка базы материалов.
        '''
        material = self.materials.get(material_id)
        if material is None:
            raise KeyError(
                f"Material id {material_id} not found for series {self.series!r}"
            )
        return material[-1]

    def get(self, material_id: int, default=None):
        return self.materials.get(material_id, default)


def get_mat_id_by_abbr(materials_base, materials_abbr: List) -> int:
    abbr_ind = 0
    result = []
    for key, lst in materials_base.items():
        if len(lst) > abbr_ind and materials_base[abbr_ind] in materials_abbr:
            result.append(key)
    return result[0] if len(result) == 1 else result


def get_mat_id_by_name(material_base, name_pattern) -> float:

    pattern = re.compile(r'(?i)' + name_pattern)
    for mat_id, (abbr, name, price) in material_base.items():
        if pattern.search(name) or pattern.search(abbr):
            return mat_id
    return None
