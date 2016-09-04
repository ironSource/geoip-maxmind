from pythonjsonlogger import jsonlogger
import config
import logging
import datetime
import socket


class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        """
        Overriding parent method to implement custom logic for adding fields.
        """
        for field in self._required_fields:
            log_record[field] = record.__dict__.get(field)
        log_record.update(message_dict)
        log_record.update({
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'host': socket.gethostname()
        })
        jsonlogger.merge_record_extra(record, log_record, reserved=self._skip_fields)


def configure_logging():
    logging.basicConfig(filename='example.log',level=logging.DEBUG)

    logger = logging.getLogger()
    handler = logging.FileHandler(config.SETTINGS['LOG_PATH'])
    formatter = JsonFormatter()

    del logger.handlers[:]

    handler.setFormatter(formatter)
    logger.addHandler(handler)