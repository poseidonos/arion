from node import node
import lib
import pos
import prerequisite


class Initiator(node.Node):
    def __init__(self, json):
        self.json = json
        self.name = json["NAME"]
        self.id = json["ID"]
        self.pw = json["PW"]
        self.nic_ssh = json["NIC"]["SSH"]
        try:
            self.prereq = json["PREREQUISITE"]
        except Exception as e:
            self.prereq = None
        self.spdk_dir = json["SPDK"]["DIR"]
        self.spdk_tp = json["SPDK"]["TRANSPORT"]
        self.output_dir = json["SPDK"]["DIR"] + "/tmp"
        self.device_list = []
        try:
            self.vdbench_dir = json["VDBENCH"]["DIR"]
        except Exception as e:
            self.vdbench_dir = ""
        self.targets = json["TARGETs"]
        self.nvme_cli = lib.nvme.Cli(json)
        self.prereq_manager = prerequisite.manager.Manager(json, self.spdk_dir)
        self.cmd_prefix = (
            f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no "
            f"{self.id}@{self.nic_ssh} sudo nohup "
        )
        self.fio_version = "not defined"

    def bring_up(self) -> None:
        lib.printer.green(f" {__name__}.bring_up start : {self.name}")

        self.prereq_manager.run()

        self.fio_version = self.sync_run("fio --version")
        lib.printer.yellow(f"fio version: {self.fio_version}")

        pos.env.remove_directory(
            self.id, self.pw, self.nic_ssh, self.output_dir)
        pos.env.make_directory(self.id, self.pw, self.nic_ssh, self.output_dir)

        self.connect_kdd()
        lib.printer.green(f" {__name__}.bring_up end : {self.name}")

    def wrap_up(self) -> None:
        self.disconnet_kdd()
        lib.printer.green(f" {__name__}.wrap_up end : {self.name}")

    def sync_run(self, cmd, ignore_err=False, sh=True):
        return lib.subproc.sync_run(f"{self.cmd_prefix}{cmd}", ignore_err, sh)

    def sync_parallel_run(self, cmd_list, ignore_err=False, sh=True):
        cmds = [f"{self.cmd_prefix}{cmd}" for cmd in cmd_list]
        return lib.subproc.sync_parallel_run(cmds, ignore_err, sh)

    def async_run(self, cmd, ignore_err=False, sh=True):
        return lib.subproc.async_run(f"{self.cmd_prefix}{cmd}", ignore_err, sh)

    def async_parallel_run(self, cmd_list, ignore_err=False, sh=True):
        cmds = [f"{self.cmd_prefix}{cmd}" for cmd in cmd_list]
        return lib.subproc.async_parallel_run(cmds, ignore_err, sh)

    def disconnet_kdd(self) -> None:
        for tgt in self.targets:
            if tgt.get("KDD_MODE") and tgt["KDD_MODE"]:
                self.disconnect_nvme(tgt)

    def connect_kdd(self) -> None:
        for tgt in self.targets:
            if tgt.get("KDD_MODE") and tgt["KDD_MODE"]:
                self.disconnect_nvme(tgt)
                self.discover_nvme(tgt)
                self.connect_nvme(tgt)
                self.list_nvme(tgt)

    def disconnect_nvme(self, target) -> None:
        for subsys in target["SUBSYSTEMs"]:
            nqn_index = subsys["NQN_INDEX"]
            for i in range(subsys["NUM_SUBSYSTEMS"]):
                nqn = f"{subsys['NQN_PREFIX']}{nqn_index:03d}"
                nqn_index += 1
                self.nvme_cli.disconnect_nqn(nqn)

    def discover_nvme(self, target) -> None:
        self.nvme_cli.discover(
            target["TRANSPORT"], target["IP"], target["PORT"])

    def connect_nvme(self, target) -> None:
        for subsys in target["SUBSYSTEMs"]:
            nqn_index = subsys["NQN_INDEX"]
            for i in range(subsys["NUM_SUBSYSTEMS"]):
                nqn = f"{subsys['NQN_PREFIX']}{nqn_index:03d}"
                nqn_index += 1
                self.nvme_cli.connect(
                    nqn, target["TRANSPORT"], target["IP"], target["PORT"])

    def list_nvme(self, target) -> None:
        device_json = self.nvme_cli.list("json")
        for device in device_json["Devices"]:
            for subsys in target["SUBSYSTEMs"]:
                sn_index = subsys["SN_INDEX"]
                find_device = False
                for i in range(subsys["NUM_SUBSYSTEMS"]):
                    sn = f"{subsys['SN_PREFIX']}{sn_index:03d}"
                    sn_index += 1
                    if sn == device["SerialNumber"]:
                        self.device_list.append(device["DevicePath"])
                        find_device = True
                        break
                if (find_device):
                    break
        print(" KDD Dev List:", self.device_list)

    def copy_output(self, timestamp, test_name, destination):
        lib.subproc.sync_run((
            f"sshpass -p {self.pw} scp {self.id}@{self.nic_ssh}:{self.output_dir}/"
            f"{timestamp}_{test_name}_{self.name} {destination}"
        ))
        lib.subproc.sync_run((
            f"sshpass -p {self.pw} scp {self.id}@{self.nic_ssh}:{self.output_dir}/"
            f"{timestamp}_{test_name}_{self.name}.eta {destination}"
        ))
        lib.subproc.sync_run((
            f"sshpass -p {self.pw} scp {self.id}@{self.nic_ssh}:{self.output_dir}/"
            f"{timestamp}_{test_name}_{self.name}*.log {destination}/log"
        ))

    def get_volume_id_of_device(self, device_list):
        volume_id_list = {}
        for key in device_list:
            cmd = f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no {self.id}@{self.nic_ssh} \
                sudo nvme list | awk '{{if ($1 == \"{key}\") print $2}}'"
            serial_number = lib.subproc.sync_run(cmd)
            volId = int(serial_number[3:])
            volume_id_list[key] = volId
        return volume_id_list
