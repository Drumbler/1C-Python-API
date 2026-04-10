from fastapi import HTTPException
# from app.modules.zvn_01 import calculate
from app.controllers.module_loader import load_module
# from app.utils.logger.logger import debug_logger


class CalculationController:
    async def calculation(self, series, parameters):
        
        try:
            print(f'Trying to load {series} module (Модуль {series} загружается)')
            module = load_module(series)
            if not hasattr(module, 'calculate'):
                raise HTTPException(
                    status_code=400, detail=f"module {series} does not support calculation (Модуль не поддерживается)")
            print(f'Модуль {series} успешно загружен!')
            print('Рассчитывается стоимость...')
            cost, markup = module.calculate(parameters, series)
            if cost is None:
                raise HTTPException(
                    status_code=400, detail=f"module {series} returned None (Модуль вернул None)")
            return cost, markup
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ImportError:
            raise HTTPException(
                status_code=404, detail=f"module {series} not found (Модуль не найден)")
