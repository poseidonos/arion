import lib


def ulimit(id, pw, ip, opt):
    lib.printer.green(f" + {__name__}.ulimit : {opt}")
    set_ulimit = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} \
        ulimit -c {opt}"
    lib.subproc.sync_run(set_ulimit)


def apport(id, pw, ip, opt):
    lib.printer.green(f" + {__name__}.apport : {opt}")
    set_apport = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} \
        /lib/systemd/systemd-sysv-install {opt} apport"
    lib.subproc.sync_run(set_apport)


def core_pattern(id, pw, ip, core_dir, core_pattern):
    lib.printer.green(
        f" + {__name__}.core_pattern : {core_dir}, {core_pattern}")
    mk_core_dir = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} \
        sudo mkdir -p {core_dir}"
    lib.subproc.sync_run(mk_core_dir)

    set_core_pattern = (
        f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} "
        f"'sudo echo {core_pattern} > /proc/sys/kernel/core_pattern'"
    )
    lib.subproc.sync_run(set_core_pattern)
