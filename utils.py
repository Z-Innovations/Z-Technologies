import subprocess
import logging
from flask import has_request_context, request

# __all__ = [
#     'construct_process_info',
#     'construct_debug_info',
#     'ColorfulFormatter',
# ]

def construct_process_info(p: subprocess.CompletedProcess):
    return f"Return code:{p.returncode}" \
            + "\nargs:" + ' '.join([f'"{a}"' for a in p.args]) \
            + (f"\nstdout:{p.stdout.decode()}" if p.stdout is not None else "") \
            + (f"\nstderr:{p.stderr.decode()}" if p.stderr is not None else "")

def construct_debug_info(name: str, *procs: subprocess.CompletedProcess, failed_at: str | None = None):
    fail_info = f"yes; at:{failed_at}" if failed_at is not None else "no"
    procs_info = "\n\n".join([construct_process_info(p) for p in procs]) if procs else None
    return f'{name} was called/requested. Did fail?: {fail_info}.' \
            + (f'\nProcess Info (total {len(procs)}):\n\n{procs_info}' if procs_info is not None else "")

class ColorfulFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    _format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + _format + reset,
        logging.INFO: grey + _format + reset,
        logging.WARNING: yellow + _format + reset,
        logging.ERROR: red + _format + reset,
        logging.CRITICAL: bold_red + _format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    

class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.original_ip = request.headers.get('CF-Connecting-IP', None) if has_request_context() else None
        return super().format(record)

# def get_db_url():
#     g = os.environ.get
#     #f'postgresql:///{os.environ.get('DB_USER', 'z-tech')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}'
#     #{os.environ.get('DB_PORT', 'localhost')}
#     if os.environ.get('DATABASE_URL') is not None:
#         return os.environ.get('DATABASE_URL')
#     url = g('DB_DIALECT', 'postgresql')
#     if g('DB_DRIVER') is not None:
#         url += f"+{g('DB_DRIVER')}"
#     url += f'://{os.environ.get('DB_USER', 'z-tech')}'
#     if g('DB_PASSWORD') is not None:
#         url += f":{g('DB_PASSWORD')}"
#     url += f"@{}"
#     url = f'postgresql://{os.environ.get('DB_USER', 'z-tech')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}'