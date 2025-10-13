import json
import time
import traceback
import logging
from uuid import uuid4
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger.Iterator_wrapper import AsyncIteratorWrapper


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, logger: logging.Logger):
        self._logger = logger
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        start_time = time.perf_counter()
        await self.set_body(request)

        try:
            response = await call_next(request)
            response.headers["X-API-Request-ID"] = request_id
        except Exception as e:
            # Извлекаем стек вызова и определяем место возникновения ошибки
            tb = traceback.extract_tb(e.__traceback__)
            last_trace = tb[-1] if tb else None
            error_location = (
                f"{last_trace.filename}:{last_trace.lineno} in {last_trace.name}"
                if last_trace else "unknown"
            )
            # Важно: первым аргументом – строка-сообщение, затем передаем extra
            self._logger.exception("Unhandled error occurred", extra={
                "location": error_location,
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
                "error": str(e)
            })
            return Response(
                content=json.dumps(
                    {"detail": "Internal server error"}, indent=4).encode("utf-8"),
                status_code=500,
                media_type="application/json",
            )

        finish_time = time.perf_counter()
        duration = finish_time - start_time

        request_data = await self.log_request(request)
        response_data = await self.log_response(response, duration)
        log_data = {
            "request_id": request_id,
            "request": request_data,
            "response": response_data,
        }
        self._logger.info("Request handled", extra=log_data)
        return response

    async def set_body(self, request: Request):
        if not hasattr(request, "_body"):
            request._body = await request.body()

        async def receive():
            return {"type": "http.request", "body": request._body}
        request._receive = receive

    async def log_request(self, request: Request):
        path = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"
        try:
            body = json.loads(request._body.decode())
        except Exception:
            body = request._body.decode() if request._body else None
        return {
            "method": request.method,
            "path": path,
            "body": body,
            "ip": request.client.host,
        }

    async def log_response(self, response: Response, duration: float):
        if hasattr(response, "body_iterator"):
            body = b"".join([chunk async for chunk in response.body_iterator])
            response.body_iterator = AsyncIteratorWrapper([body])
        else:
            body = response.body
        return {
            "status_code": response.status_code,
            "execution_time": f"{duration:.4f}s",
            "body": body.decode("utf-8") if body else None,
        }
