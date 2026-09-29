import importlib

from logging import getLogger
from app.data.database_pool import pool
import os


logger = getLogger(__name__)

def unpack_and_merge(dict1: dict, dict2: dict) -> dict:
    """
    Распаковывает ключи второго словаря (списки) и добавляет их в первый словарь.

    :param dict1: Первый словарь, в который будут добавлены распакованные ключи.
    :param dict2: Второй словарь, содержащий списки(tuple) в качестве ключей.
    :return: Обновленный первый словарь.
    """
    for keys, value in dict2.items():
        # Каждый элемент списка становится отдельным ключом в первом словаре
        for key in keys:
            dict1[key] = value
    return dict1


def load_module_by_path(file_location: str):
    try:
        module = importlib.import_module(f"app.modules.{file_location}")
        return module
    except ImportError as e:
        logger.warning(f"Module not found (Модуль не найден): {e}")
        raise ImportError(f"module {file_location} not found (Модуль не найден)") from e
    


def load_module(series: str):
    from app.data.DBrepository import DBrepository

    DBrepo = DBrepository(pool)
    # series_lib_unpacked = {
    #     (
    #         'ЗВН-01', 'ЗВН-02', 'ЗВН-03', 'ЗВН-04/03',
    #         'ЗВН-05', 'ЗВН-04/01', 'ЗВН-04/02', 'ЗВН-04/05',
    #         'ЗВН-01 ПРЕМИУМ', 'ЗВН-02 ПРЕМИУМ', 'ЗВН-03 ПРЕМИУМ', 'ЗВН-04/03 ПРЕМИУМ',
    #         'ЗВН-05 ПРЕМИУМ', 'ЗВН-04/01 ПРЕМИУМ', 'ЗВН-04/02 ПРЕМИУМ', 'ЗВН-04/05 ПРЕМИУМ',
    #         'ЗПВН-01', 'ЗПВН-02', 'ЗПВН-03', 'ЗПВН-04/03',
    #         'ЗПВН-05', 'ЗПВН-04/01', 'ЗПВН-04/02', 'ЗПВН-04/05',
    #         'ЗПВН-01 ПРЕМИУМ', 'ЗПВН-02 ПРЕМИУМ', 'ЗПВН-03 ПРЕМИУМ', 'ЗПВН-04/03 ПРЕМИУМ',
    #         'ЗПВН-05 ПРЕМИУМ', 'ЗПВН-04/01 ПРЕМИУМ', 'ЗПВН-04/02 ПРЕМИУМ', 'ЗПВН-04/05 ПРЕМИУМ'
    #     ): 'zonts.zonts',
    #     (
    #         'ВМЛ-1', 'ВМЛ-2', 'ВМЛ-3', 'ВМЛЦ-1', 'ВМЛЦ-2', 'ВМЛЦ-3', 'ВМЛС-1', 'ВМЛСЦ-1',
    #         'ВМБ-1', 'ВМБ-2', 'ВМБ-3', 'ВМБЦ-1', 'ВМБЦ-2', 'ВМБЦ-3', 'ВМБС-1', 'ВМБСЦ-1',
    #         'ВМН-1', 'ВМН-2', 'ВМН-3', 'ВМНЦ-1', 'ВМНЦ-2', 'ВМНЦ-3', 'ВМНС-1', 'ВМНСЦ-1',
    #         'ВМЭ-1', 'ВМЭ-2', 'ВМЭ-3', 'ВМЭЦ-1', 'ВМЭЦ-2', 'ВМЭЦ-3', 'ВМЭС-1', 'ВМЭСЦ-1',
    #         'ВМП-1', 'ВМП-2', 'ВМП-3', 'ВМПЦ-1', 'ВМПЦ-2', 'ВМПЦ-3', 'ВМПС-1', 'ВМПСЦ-1',
    #         'ВКЛ-1', 'ВКЛ-2', 'ВКЛ-3', 'ВКЛЦ-1', 'ВКЛЦ-2', 'ВКЛЦ-3', 'ВКЛС-1', 'ВКЛСЦ-1',
    #         'ВКБ-1', 'ВКБ-2', 'ВКБ-3', 'ВКБЦ-1', 'ВКБЦ-2', 'ВКБЦ-3', 'ВКБС-1', 'ВКБСЦ-1',
    #         'ВКН-1', 'ВКН-2', 'ВКН-3', 'ВКНЦ-1', 'ВКНЦ-2', 'ВКНЦ-3', 'ВКНС-1', 'ВКНСЦ-1',
    #         'ВКЭ-1', 'ВКЭ-2', 'ВКЭ-3', 'ВКЭЦ-1', 'ВКЭЦ-2', 'ВКЭЦ-3', 'ВКЭС-1', 'ВКЭСЦ-1',
    #         'ВКП-1', 'ВКП-2', 'ВКП-3', 'ВКПЦ-1', 'ВКПЦ-2', 'ВКПЦ-3', 'ВКПС-1', 'ВКПСЦ-1',
    #     ): 'baths.vmn',
    #     ('СТЕЛЛАЖ СТПБ', 'СТЕЛЛАЖ СТПЛ', 'СТЕЛЛАЖ СТПН', 'СТЕЛЛАЖ СТПУ',
    #      'СТЕЛЛАЖ СТПЭ', 'СТЕЛЛАЖ СТПП', 'СТЕЛЛАЖ СТПС', 'СТЕЛЛАЖ СТПЭР',
    #      'СТЕЛЛАЖ СТППР', 'СТЕЛЛАЖ СТПСР'):  'shelvings.stpx',
    # }
    # series_lib = {
    #     'СТЕЛЛАЖ СТППР': 'shelvings.stpx', 'СТЕЛЛАЖ СТПЭР': 'shelvings.stpx', 'СТЕЛЛАЖ СТПН': 'shelvings.stpx', 'СТЕЛЛАЖ СТПЛ': 'shelvings.stpx',
    #     'СТЕЛЛАЖ СТПБ': 'shelvings.stpx', 'СТЕЛЛАЖ СТПП': 'shelvings.stpx', 'СТЕЛЛАЖ СТПЭ': 'shelvings.stpx', 'СТПНП': 'shelvings.stpxP',
    #     'СТПЛП': 'shelvings.stpxP', 'СТПБП': 'shelvings.stpxP', 'СППР': 'tables.spx', 'СПЭР': 'tables.spx', 'СПН': 'tables.spx',
    #     'СПЛ': 'tables.spx', 'СПБ': 'tables.spx', 'СПП': 'tables.spx', 'СПЭ': 'tables.spx'
    # }
    

    # series_lib = unpack_and_merge(series_lib, series_lib_unpacked)
    try:
        file_loc = DBrepo.get_module_file_location(series)
        # ser = series
        # ser = ser.upper()
        module = importlib.import_module(
            f"app.modules.{file_loc}")
        return module
    except LookupError as e:
        logger.warning(f"Module not found (Модуль не найден): {e}")
        raise ImportError(f"module {series} not found (Модуль не найден)") from e
    except ModuleNotFoundError as e:
        logger.warning(f"Module not found (Модуль не найден): {e}")
        raise ImportError(f"module {series} not found (Модуль не найден)")
    except Exception as e:
        logger.warning(f"Error while loading module (Возникла ошибка при расчете): {e}")
        raise ImportError(f"Error while loading module (Возникла ошибка при загрузке модуля): {e}")


def load_all_modules():
    # Get the directory containing components
    components_dir = 'app/modules/components'

    # Dict to store loaded modules
    modules = {}

    # Check if directory exists
    if not os.path.exists(components_dir):
        return modules

    # Iterate through all .py files in components directory
    for filename in os.listdir(components_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            # Get module name without .py extension
            module_name = filename[:-3]

            try:
                # Import the module using importlib
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    os.path.join(components_dir, filename)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Add loaded module to list
                modules[module_name] = module

            except Exception as e:
                logger.warning(f"Error loading module {module_name}: {e}")
                continue

    return modules
