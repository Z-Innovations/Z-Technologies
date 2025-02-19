from enum import Enum
import subprocess
import logging

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

class AnsiStyleCode(Enum):
    bold = 1
    red = 31
    green = 32
    yellow = 33
    magenta = 35
    cyan = 36

def ansi_style(value: str, *styles: str) -> str:
    for style in styles:
        value = f"\x1b[{AnsiStyleCode[style].value}m{value}"

    return f"{value}\x1b[0m"

def colorify_request(msg: str, status: int | str):
    status = str(status)
    match status:
        case '200': # Success
            return msg
        case '304': # Resource Not Modified
            return ansi_style(msg, 'cyan')
        case '404': # Resource Not Found
            return ansi_style(msg, 'yellow')
    match status[0]:
        case '1': # Informational
            return ansi_style(msg, 'bold')
        case '3': # Redirection
            return ansi_style(msg, 'green')
        case '4': # Client Error
            return ansi_style(msg, 'bold', 'red')
    return ansi_style(msg, 'bold', 'magenta') # 5xx Server Error or anything else

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