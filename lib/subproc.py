from concurrent import futures
from typing import Union, List

import lib
import lib.thread
import subprocess

subproc_log = False


def set_print_log(log_option):
    global subproc_log
    subproc_log = log_option


def print_log(command):
    if (subproc_log):
        lib.printer.yellow(command)


def sync_run(command: Union[str, list], ignore_err: bool = False, shell: bool = True) -> str:
    """ Execute command and wait utill done.

    Args:
        command (Union[str, list]): Will be executed by subprocess library.
        ignore_err (bool, optional): Ignore command result error. Defaults to False.
        shell (bool, optional): If False, command has to be split within a list. Defaults to True.

    Returns:
        str: command result message
    """
    print_log(command)
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell
    )
    (out, err) = proc.communicate()
    err_str = err.decode("utf-8")
    if not ignore_err and 0 < len(err_str):
        lib.printer.red(command)
        raise Exception(err_str)
    return out.decode("utf-8")


def sync_parallel_run(cmd_list: List[Union[str, list]], ignore_err: bool = False, shell: bool = True) -> List[str]:
    """ Execute multiple commands simultaneously and wait all command done.
    Commands will be executed in a ThreadPoolExecutor

    Args:
        cmd_list (List[str | list]): Will be executed by subprocess library.
        ignore_err (bool, optional): Ignore command result error. Defaults to False.
        shell (bool, optional): If False, command has to be split within a list. Defaults to True.

    Returns:
        List[str]: commands result message
    """
    results = []
    with futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(sync_run, cmd, ignore_err, shell)
                 for cmd in cmd_list]
    for task in futures.as_completed(tasks):
        results.append(task.result())
    return results


def async_run(command: Union[str, list], ignore_err: bool = False, shell: bool = True) -> lib.thread.ThreadReturnable:
    """ Execute command on a new thread and don't wait the result.

    Args:
        command (Union[str, list]): Will be executed by subprocess library.
        ignore_err (bool, optional): Ignore command result error. Defaults to False.
        shell (bool, optional): If False, command has to be split within a list. Defaults to True.

    Returns:
        lib.thread.ThreadReturnable: To wait the result, use join()
    """
    thread = lib.thread.ThreadReturnable(target=sync_run,
                                         args=(command, ignore_err, shell))
    thread.start()
    return thread


def async_parallel_run(cmd_list: List[Union[str, list]], ignore_err: bool = False, shell: bool = True) -> List[lib.thread.ThreadReturnable]:
    """ Execute multiple commands simultaneously and don't wait the results.

    Args:
        cmd_list (List[Union[str, list]]): Will be executed by subprocess library.
        ignore_err (bool, optional): Ignore command result error. Defaults to False.
        shell (bool, optional): If False, command has to be split within a list. Defaults to True.

    Returns:
        List[lib.thread.ThreadReturnable]: To wait the result, reference this code: [thread.join() for thread in return_value_of_async_parallel_run]
    """
    threads = [lib.thread.ThreadReturnable(target=sync_run,
                                           args=(cmd, ignore_err, shell))
               for cmd in cmd_list]
    [thread.start() for thread in threads]
    return threads
