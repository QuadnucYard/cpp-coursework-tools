import subprocess
from pathlib import Path

import rich
from result import Err, Ok, Result

from . import results as R
from .utils import auto_decode, trunc_lines

console = rich.get_console()


class TestRunner:
    def __init__(self, time_limit: float, output_trunc: int = 100) -> None:
        self.time_limit = time_limit
        self.output_trunc = output_trunc

    def run(self, exe: Path, stdin: str) -> Result[str, R.RE | R.TLE | R.UKE]:
        try:
            p = subprocess.Popen(exe, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                stdout, stderr = p.communicate(stdin.encode(), timeout=self.time_limit)
            except subprocess.TimeoutExpired as e:
                p.kill()
                p.communicate()
                return Err(R.TLE(str(e)))
            if stderr:
                return Err(R.RE(auto_decode(stderr)))
            p.terminate()
            return Ok(trunc_lines(auto_decode(stdout), self.output_trunc))
        except Exception as e:
            return Err(R.UKE(str(e)))
