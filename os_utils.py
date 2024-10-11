import subprocess
from typing import Union

from external import log


def run(cmd: Union[list, str]):
    if isinstance(cmd, list):
        log.info(f"Run command: {' '.join(cmd)}")
    else:
        log.info(f"Run command: {cmd}")
    try:
        popen = subprocess.Popen(cmd)
    except subprocess.SubprocessError as e:
        log.error(f"Run command error: {e}")
        return None, str(e)
    return popen.pid, None
