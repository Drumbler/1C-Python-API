from pydantic import BaseModel, Field


class CalculationRequest(BaseModel):
    series: str = Field(..., description="Серия для выбора модуля")
    parameters: str = Field(...,
                            description="Характеристики продукции (без слеша в начале)")


class CalculationResponse(BaseModel):
    cost: float = Field(..., description="Рассчитанная себестоимость")
    markup: float = Field(..., description="Рассчитанная наценка")

