import subprocess
import time


class SlurmError(Exception):
    """ Errors related to Slurm. """


def shexecute(cmd):
    """ Run a command and yield output line by line. """
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def shexecute_remote(cmd, host):
    """ Run a command on a remote server and yield output line by line. """
    return shexecute(["ssh", host, cmd])


def slurm_submit(script, *args):
    """ Submit a job. """
    for line in shexecute(["sbatch", script, *args]):
        print(line, end="")
        if line.startswith("Submitted batch job "):
            jobid = int(line.split()[-1])
            return jobid
    raise SlurmError("Could not submit job")


def slurm_check(jobid: int):
    """ Check the status of a job. 
    Returns:
        bool: True if job is still running, False otherwise
    """
    for line in shexecute(["squeue", "-j", str(jobid)]):
        print(line, end="")
        if line.startswith(str(jobid)):
            return True
    return False


def slurm_wait(jobid, interval=60, timeout=60*60*6):
    """
    Wait for a job to finish.
    
    Args:
        interval (int): seconds between checks (default 60 seconds)
        timeout (int): seconds before timeout (default 6 hours)
    """
    t = time.time()
    while slurm_check(jobid):
        if time.time() - t > timeout:
            raise SlurmError(f"Job {jobid} timed out")
        time.sleep(interval)


def slurm_cancel(jobid):
    """ Cancel a job. """
    for line in shexecute(["scancel", str(jobid)]):
        print(line, end="")
