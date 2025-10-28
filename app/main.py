import logging
import traceback
import logging.config
from fastapi import FastAPI, HTTPException, Response, UploadFile
from pandas.errors import ParserError


from app.controllers.calculation_controller import CalculationController
from app.controllers.exception_handler import ErrorHandlerMiddleware
from app.schemas import CalculationRequest, CalculationResponse
from app.data.DBrepository import DBRepository
import app.logger.log_config
from app.logger.logger import LoggingMiddleware
# warning_logger, debug_logger, calculation_logger


DBrepo = DBRepository()
app = FastAPI()
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware, logger=logging.getLogger(__name__))

logger = logging.getLogger(__name__)

calc_controller = CalculationController()


@app.post("/calculate", response_model=CalculationResponse)
async def calculate_cost(request: CalculationRequest):
    if not request.series or (not request.series and not request.parameters):
        logger.error(f'Series are required')
        raise HTTPException(status_code=400, detail="Series are required")
    if not request.parameters:
        logger.error(f'Parameters are required')
        raise HTTPException(status_code=400, detail="Parameters are required")

    try:
        cost = await calc_controller.calculation(request.series, request.parameters)

        # Логируем успешный запрос в файл calculation_requests.log
        logger.info(f"Successful calculation: {cost}", extra={
            "request": request.model_dump(),
            "response": cost
        })

        return {'cost': cost}

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
        file_location = DBrepo.get_module_file_location(series)
        print(file_location, type(file_location))
        return {'file_location': file_location}
    except:
        raise HTTPException(status_code=404, detail='Module not found')


@app.post('/add_data')
async def add_data_to_db(excel_file: UploadFile):
    """
    (Временно, потом дополним) Добавление данных в базу данных
    """
    try:

        DBrepo.add_data_from_excel(excel_file)
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
        DBrepo.update_data_from_excel(excel_file)
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
