import logging
import os
import traceback
from fastapi import FastAPI, HTTPException, Response, UploadFile
from pandas.errors import ParserError
from redis.exceptions import RedisError

from app.data.calculation_cache import CalculationCache
from app.data.redis_client import redis_client
from app.controllers.calculation_controller import CalculationController
from app.controllers.exception_handler import ErrorHandlerMiddleware
from app.schemas import CalculationRequest, CalculationResponse
from app.data.DBrepository import DBrepository
import app.logger.log_config
from app.logger.logger import LoggingMiddleware
from app.data.database_pool import pool
from contextlib import asynccontextmanager
# warning_logger, debug_logger, calculation_logger

calculation_cache = CalculationCache(
    redis_client=redis_client,
    ttl_seconds=int(os.getenv('CALCULATION_CACHE_TTL', 21600))
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await pool.open(wait=True)
        try:
            await redis_client.ping()
            logger.info("Redis connection established successfully.")
        except RedisError as e:
            logger.warning(f"Redis is unavailable: {e}. Continuing without Redis.", exc_info=True)

        yield
    finally:
        await redis_client.aclose()
        await pool.close()

app = FastAPI(lifespan=lifespan)
repository = DBrepository(pool)

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware, logger=logging.getLogger(__name__))

logger = logging.getLogger(__name__)

calc_controller = CalculationController(repository)


@app.post("/calculate", response_model=CalculationResponse)
async def calculate_cost(request: CalculationRequest):
    if not request.series or (not request.series and not request.parameters):
        logger.error(f'Series are required')
        raise HTTPException(status_code=400, detail="Series are required")
    if not request.parameters:
        logger.error(f'Parameters are required')
        raise HTTPException(status_code=400, detail="Parameters are required")

    try:
        calculated_cost = await repository.get_calculated_product_cost_async(
            request.series,
            request.parameters,
        )
        if calculated_cost is not None:
            logger.info("Successful lookup in calculated_products", extra={
                "request": request.model_dump(),
                "response": calculated_cost,
            })
            return {'cost': calculated_cost}

        cost = await calc_controller.calculation(request.series, request.parameters)
        
        # Логируем успешный запрос в файл calculation_requests.log
        logger.info(f"Successful calculation: {cost}", extra={
            "request": request.model_dump(),
            "response": cost
        })
        
        return {'cost': cost}

    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Unknown Module. ValueError: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:

        tb = traceback.extract_tb(e.__traceback__)
        last_trace = tb[-1] if tb else None
        error_location = f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}" if last_trace else "unknown"
        logger.exception("Unhandled exception during calculation", extra={
                         "location": error_location})
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get('/series_file')
async def get_series_file(series: str):
    try:
        file_location = await repository.get_module_file_location_async(series)
        print(file_location, type(file_location))
        return {'file_location': file_location}
    except LookupError as e:
        raise HTTPException(status_code=404, detail=f'Module not found: {str(e)}')


@app.post('/add_data')
async def add_data_to_db(excel_file: UploadFile):
    """
    (Временно, потом дополним) Добавление данных в базу данных
    """
    try:

        await repository.add_data_from_excel(excel_file)
        return Response(status_code=200)
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        last_trace = tb[-1] if tb else None
        error_location = f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}" if last_trace else "unknown"
        logger.error(f"Unhandled exception during adding data: {e}", extra={
                     'location': error_location})
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/update_data')
async def update_data_db(excel_file: UploadFile):
    """
    (Временно, потом дополним) Обновление данных в базе данных
    """
    try:
        repository.update_data_from_excel(excel_file)
        return Response(status_code=200)
    except KeyError as e:
        logger.error(f"Key error: {e}")
        raise HTTPException(
            status_code=400, detail=f'KeyError: Module {str(e)} not found')

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=f'FileNotFound: {str(e)}')

    except ParserError as e:
        logger.error(f"Error while reading excel: {e}")
        raise HTTPException(
            status_code=400, detail=f'Error while reading excel file: {str(e)}')

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        last_trace = tb[-1] if tb else None
        error_location = f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}" if last_trace else "unknown"
        logger.error(f"Unhandled exception during updating data: {e}", extra={
                     'location': error_location})
        raise HTTPException(
            status_code=500, detail=f'Unhandled exception during updating data: {str(e)}')


@app.get("/ping")
async def ping():
    return {"message": "pong"}
