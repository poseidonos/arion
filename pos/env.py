import lib


def is_pos_running(id, pw, ip, bin) -> bool:
    ps_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} sudo ps -e | grep {bin}"
    result = lib.subproc.sync_run(ps_cmd)
    if -1 == result.find(bin):
        return False
    else:
        return True


def kill_pos(id, pw, ip, bin) -> None:
    pkill_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} sudo pkill -9 {bin}"
    lib.subproc.sync_run(pkill_cmd)


def dump_pos(id, pw, ip, bin) -> None:
    pkill_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} sudo pkill -SIGQUIT {bin}"
    lib.subproc.sync_run(pkill_cmd)


def copy_pos_config(id, pw, ip, dir, cfg) -> None:
    copy_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} sudo cp {dir}/config/{cfg} /etc/pos/pos.conf"
    lib.subproc.sync_run(copy_cmd)


def execute_pos(id, pw, ip, bin, dir, log, asan_opt) -> None:
    exe_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} 'sudo "
    if "" != asan_opt:
        exe_cmd += f"ASAN_OPTIONS={asan_opt}"
    exe_cmd += f" {dir}/bin/{bin}"
    if "" != log:
        exe_cmd += f" >> {dir}/script/{log}'"
    else:
        exe_cmd += "'"
    return lib.subproc.async_run(exe_cmd, True)


def remove_directory(id, pw, ip, dir) -> None:
    rm_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} sudo rm -rf {dir}"
    lib.subproc.sync_run(rm_cmd)


def make_directory(id, pw, ip, dir) -> None:
    mkdir_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} sudo mkdir -p {dir}"
    lib.subproc.sync_run(mkdir_cmd)


def detach_device(id, pw, ip, dev) -> None:
    detach_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} 'sudo echo 1 > /sys/bus/pci/devices/{dev}/remove'"
    lib.subproc.sync_run(detach_cmd)


def pcie_scan(id, pw, ip) -> None:
    scan_cmd = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} 'sudo echo 1 > /sys/bus/pci/rescan'"
    lib.subproc.sync_run(scan_cmd)
