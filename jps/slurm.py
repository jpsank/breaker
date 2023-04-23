import subprocess
from dataclasses import dataclass
import time

from jps.util import *


class SlurmError(Exception):
    """ Errors related to Slurm. """


def execute(cmd):
    """ Run a command and yield output line by line. """
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


@dataclass
class SlurmJob:
    id: int

    @staticmethod
    def submit(script, *args):
        """ Submit a job. """
        for line in execute(["sbatch", script, *args]):
            print(line, end="")
            if line.startswith("Submitted batch job "):
                jobid = int(line.split()[-1])
                return SlurmJob(jobid)
        raise SlurmError("Could not submit job")

    def check(self):
        """ Check the status of a job. 
        Returns:
            bool: True if job is still running, False otherwise
        """
        for line in execute(["squeue", "-j", str(self.id)]):
            print(line, end="")
            if line.startswith(str(self.id)):
                return True
        return False

    def wait(self, interval=60, timeout=60*60*6):
        """
        Wait for a job to finish.
        
        Args:
            interval (int): seconds between checks (default 60 seconds)
            timeout (int): seconds before timeout (default 6 hours)
        """
        t = time.time()
        while self.check():
            if time.time() - t > timeout:
                raise SlurmError(f"Job {self.id} timed out")
            time.sleep(interval)
    
    def cancel(self):
        """ Cancel a job. """
        for line in execute(["scancel", str(self.id)]):
            print(line, end="")

