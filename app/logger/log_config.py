import logging
import logging.config
from app.logger.json_formatter import IndentedJsonFormatter

# Фильтр для логов ниже уровня WARNING (например, DEBUG и INFO)


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.WARNING

# Фильтр для логов уровня WARNING и выше


class WarningErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.WARNING

class SuccessFilter(logging.Filter):
    def filter(self, record):
        return (
            record.levelno == logging.INFO
            and record.getMessage().startswith("Successful calculation")
            and hasattr(record, 'response')
        )



logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            # Используем кастомный JSON форматтер, который выводит extra поля
            "()": "app.utils.logger.json_formatter.IndentedJsonFormatter",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "filters": {
        "info_filter": {
            "()": InfoFilter
        },
        "warning_error_filter": {
            "()": WarningErrorFilter
        },
        "success_filter": {
            "()": SuccessFilter
        }
    },
    "handlers": {
        "info_file": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": "app/data/logs/info.log",
            "encoding": "utf8",
            # Применяем фильтр: пропускать только логи ниже WARNING
            "filters": ["info_filter"]
        },
        "error_file": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": "app/data/logs/errors.log",
            "encoding": "utf8",
            # Применяем фильтр: пропускать только логи с уровнем WARNING и выше
            "filters": ["warning_error_filter"]
        },
        "calculation_requests_file": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": "app/data/logs/calculation_requests.log",
            "encoding": "utf8",
            # Применяем фильтр: пропускать только успешные логи с ответом
            "filters": ["success_filter"]
        }
    },
    "root": {
        "handlers": ["info_file", "error_file"],
        "level": "DEBUG",
    },
    "loggers": {
        "app": {
            "handlers": ["info_file", "error_file", "calculation_requests_file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

try:
    logging.config.dictConfig(logging_config)
    print("Logging configuration applied successfully")
except Exception as e:
    print(f"Error applying logging configuration: {e}")
