# app/utils/logger/json_formatter.py
import json
import logging


class IndentedJsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Добавляем дополнительные атрибуты, если они присутствуют
        extra_keys = ['location', 'path', 'method',
                      'error', 'request_id', 'request',
                      'response']
        for key in extra_keys:
            value = getattr(record, key, None)
            if value is not None:
                log_record[key] = value

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, indent=4, ensure_ascii=False)
