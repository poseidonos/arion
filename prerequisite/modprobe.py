import lib


def modprobe(id, pw, ip, opt):
    lib.printer.green(f" + {__name__}.modprobe : {opt}")
    for mod in opt:
        modprobe = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} \
            sudo modprobe {mod}"
        lib.subproc.sync_run(modprobe)
