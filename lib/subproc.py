from concurrent import futures
import lib
import subprocess

subproc_log = False


def set_print_log(log_option):
    global subproc_log
    subproc_log = log_option


def print_log(cmd):
    if (subproc_log):
        lib.printer.yellow(cmd)


def sync_run(cmd, ignore_err=False, sh=True):
    print_log(cmd)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=sh
    )
    (out, err) = proc.communicate()
    err_str = err.decode("utf-8")
    if not ignore_err and 0 < len(err_str):
        lib.printer.red(cmd)
        raise Exception(err_str)
    return out.decode("utf-8")


def sync_parallel_run(cmd_list, ignore_err=False, sh=True):
    results = []
    with futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(sync_run, cmd, ignore_err, sh)
                 for cmd in cmd_list]
    for task in futures.as_completed(tasks):
        results.append(task.result())
    return results


def async_run(cmd, ignore_err=False, sh=True):
    thread = lib.thread.ThreadReturnable(target=sync_run,
                                         args=(cmd, ignore_err, sh))
    thread.start()
    return thread


def async_parallel_run(cmd_list, ignore_err=False, sh=True):
    threads = [lib.thread.ThreadReturnable(target=sync_run,
                                           args=(cmd, ignore_err, sh))
               for cmd in cmd_list]
    [thread.start() for thread in threads]
    return threads
