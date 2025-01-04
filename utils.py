import subprocess

__all__ = [
    #'construct_process_info',
    'construct_debug_info',
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