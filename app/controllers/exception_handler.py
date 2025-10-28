import traceback
from logging import getLogger
from sqlite3 import DatabaseError
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

logger = getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        client_ip = request.client.host

        try:
            response = await call_next(request)
            logger.info(
                f"Request: {request.method} {request.url} | Client IP: {client_ip}"
            )
            return response

        except Exception as e:
            # Вычисляем место возникновения ошибки
            tb = traceback.extract_tb(e.__traceback__)
            last_trace = tb[-1] if tb else None
            error_location = (
                f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}"
                if last_trace else "unknown"
            )
            # Логируем ошибку с дополнительным полем location через extra
            logger.error(
                f"Unhandled exception during calculation: {e} | Client IP: {client_ip}",
                extra={"location": error_location, 
                       "client_ip": client_ip},
                exc_info=True
            )
            request_body = await request.body()
            logger.error(
                f"Request body: {request_body} Exception: {e} | Client IP: {client_ip}",
                extra={"location": error_location, 
                       "client_ip": client_ip},
                exc_info=True
            )
            raise HTTPException(status_code=500, detail=str(e))

        except ValueError as ve:
            tb = traceback.extract_tb(ve.__traceback__)
            last_trace = tb[-1] if tb else None
            error_location = (
                f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}"
                if last_trace else "unknown"
            )
            warning_message = f"Unknown Module. ValueError: {ve} | Client IP: {client_ip}"
            logger.warning(warning_message, extra={
                           "location": error_location, 
                           "client_ip": client_ip})
            raise HTTPException(status_code=404, detail=str(ve))

        except DatabaseError as db_err:
            tb = traceback.extract_tb(db_err.__traceback__)
            last_trace = tb[-1] if tb else None
            error_location = (
                f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}"
                if last_trace else "unknown"
            )
            warning_message = f"Database error: {db_err} | Client IP: {client_ip}"
            logger.warning(warning_message, extra={
                           "location": error_location, 
                           "client_ip": client_ip})
            raise HTTPException(status_code=500, detail=str(db_err))

        except RequestValidationError as rve:
            tb = traceback.extract_tb(rve.__traceback__)
            last_trace = tb[-1] if tb else None
            error_location = (
                f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}"
                if last_trace else "unknown"
            )
            warning_message = f"Request validation error: {rve} | Client IP: {client_ip}"
            logger.warning(warning_message, extra={
                           "location": error_location, 
                           "client_ip": client_ip})
            raise HTTPException(status_code=422, detail=str(rve))
