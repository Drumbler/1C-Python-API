from dataclasses import dataclass

from fastapi import HTTPException

from app.controllers.module_loader import load_module


@dataclass(slots=True)
class CalculationDetails:
    cost: float
    markup: float | None = None


def _normalize_calculation_result(result: object, series: str) -> CalculationDetails:
    if result is None:
        raise HTTPException(
            status_code=400,
            detail=f"module {series} returned None (Модуль вернул None)",
        )

    if isinstance(result, tuple):
        if not result:
            raise HTTPException(
                status_code=400,
                detail=f"module {series} returned empty result (Модуль вернул пустой результат)",
            )

        cost = float(result[0])
        markup = float(result[1]) if len(result) > 1 and result[1] is not None else None
        return CalculationDetails(cost=cost, markup=markup)

    return CalculationDetails(cost=float(result))


class CalculationController:
    async def calculation(self, series, parameters):
        details = self.get_calculation_details(series, parameters)
        return details.cost

    def get_calculation_details(self, series, parameters) -> CalculationDetails:
        try:
            print(f'Trying to load {series} module (Модуль {series} загружается)')
            module = load_module(series)
            print(f'Модуль {series} успешно загружен!')
            print('Рассчитывается стоимость...')
            if hasattr(module, 'calculate_details'):
                calculation_result = module.calculate_details(parameters, series)
            elif hasattr(module, 'calculate'):
                calculation_result = module.calculate(parameters, series)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"module {series} does not support calculation (Модуль не поддерживается)",
                )
            return _normalize_calculation_result(calculation_result, series)
        except ImportError as exc:
            status_code = 404 if 'not found' in str(exc).casefold() else 400
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
