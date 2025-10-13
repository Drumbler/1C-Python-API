from fastapi import HTTPException
# from app.modules.zvn_01 import calculate
from app.utils.handlers.module_loader import load_module
# from app.utils.logger.logger import debug_logger


class CalculationController:
    async def calculation(self, series, parameters):
        
        try:
            module = load_module(series)
            if not hasattr(module, 'calculate'):
                raise HTTPException(
                    status_code=400, detail=f"module {series} does not support calculation")
            cost = module.calculate(parameters, series)
            if cost is None:
                raise HTTPException(
                    status_code=400, detail=f"module {series} returned None")
            return cost
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ImportError:
            raise HTTPException(
                status_code=404, detail=f"module {series} not found")
