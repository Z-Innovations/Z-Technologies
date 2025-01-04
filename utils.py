import subprocess
import logging

__all__ = [
    'construct_process_info',
    'construct_debug_info',
    'ColorfulFormatter',
]

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