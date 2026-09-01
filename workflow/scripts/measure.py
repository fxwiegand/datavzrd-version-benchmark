import os
import shutil
import tempfile
import time

spec = snakemake.input.spec
repeats = int(snakemake.params.repeats)
scratch = snakemake.resources.tmpdir

runs = []
for _ in range(repeats):
    output = tempfile.mkdtemp(dir=scratch, prefix="datavzrd_")
    start = time.monotonic()
    pid = os.fork()
    if pid == 0:
        null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(null, 1)
        os.dup2(null, 2)
        os.execvp("datavzrd", ["datavzrd", spec, "--output", output, "--overwrite-output"])
        os._exit(127)
    _, status, usage = os.wait4(pid, 0)
    seconds = time.monotonic() - start
    shutil.rmtree(output, ignore_errors=True)
    if not (os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0):
        raise RuntimeError("datavzrd did not finish successfully")
    runs.append((seconds, usage.ru_maxrss / 1024))

with open(snakemake.output[0], "w") as handle:
    handle.write("run\tseconds\tpeak_mb\n")
    for index, (seconds, peak) in enumerate(runs, 1):
        handle.write(f"{index}\t{seconds:.3f}\t{peak:.1f}\n")
