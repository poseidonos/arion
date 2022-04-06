import json
import lib
import pos
import prerequisite


class Initiator:
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

    def Prepare(self) -> None:
        lib.printer.green(f" {__name__}.Prepare : {self.name}")
        if (self.prereq and self.prereq["CPU"]["RUN"]):
            prerequisite.cpu.Scaling(
                self.id, self.pw, self.nic_ssh, self.prereq["CPU"]["SCALING"])
        if (self.prereq and self.prereq["MEMORY"]["RUN"]):
            prerequisite.memory.MaxMapCount(
                self.id, self.pw, self.nic_ssh, self.prereq["MEMORY"]["MAX_MAP_COUNT"])
            prerequisite.memory.DropCaches(
                self.id, self.pw, self.nic_ssh, self.prereq["MEMORY"]["DROP_CACHES"])
        if (self.prereq and self.prereq["NETWORK"]["RUN"]):
            prerequisite.network.IrqBalance(
                self.id, self.pw, self.nic_ssh, self.prereq["NETWORK"]["IRQ_BALANCE"])
            if self.prereq["NETWORK"].get("TCP_TUNE"):
                prerequisite.network.TcpTune(
                    self.id, self.pw, self.nic_ssh, self.prereq["NETWORK"]["TCP_TUNE"])
            prerequisite.network.Nic(
                self.id, self.pw, self.nic_ssh, self.prereq["NETWORK"]["NICs"])
        if (self.prereq and self.prereq["MODPROBE"]["RUN"]):
            prerequisite.modprobe.Modprobe(
                self.id, self.pw, self.nic_ssh, self.prereq["MODPROBE"]["MODs"])
        if (self.prereq and self.prereq["SPDK"]["RUN"]):
            prerequisite.spdk.Setup(
                self.id, self.pw, self.nic_ssh, self.prereq["SPDK"], self.spdk_dir)

        pos.env.remove_directory(
            self.id, self.pw, self.nic_ssh, self.output_dir)
        pos.env.make_directory(self.id, self.pw, self.nic_ssh, self.output_dir)

        self.ConnectKDD()
        lib.printer.green(f" '{self.name}' prepared")

    def Wrapup(self) -> None:
        self.DisconnetKDD()
        lib.printer.green(f" '{self.name}' wrapped up")

    def DisconnetKDD(self) -> None:
        for tgt in self.targets:
            if tgt.get("KDD_MODE") and tgt["KDD_MODE"]:
                self.DisconnectNvme(tgt)

    def ConnectKDD(self) -> None:
        for tgt in self.targets:
            if tgt.get("KDD_MODE") and tgt["KDD_MODE"]:
                self.DisconnectNvme(tgt)
                self.DiscoverNvme(tgt)
                self.ConnectNvme(tgt)
                self.ListNvme(tgt)

    def DisconnectNvme(self, target) -> None:
        for subsys in target["SUBSYSTEMs"]:
            nqn_index = subsys["NQN_INDEX"]
            for i in range(subsys["NUM_SUBSYSTEMS"]):
                nqn = f"{subsys['NQN_PREFIX']}{nqn_index:03d}"
                nqn_index += 1
                cmd = f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no {self.id}@{self.nic_ssh} \
                    sudo nvme disconnect -n {nqn}"
                lib.subproc.sync_run(cmd)

    def DiscoverNvme(self, target) -> None:
        cmd = f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no {self.id}@{self.nic_ssh} \
                    sudo nvme discover -t {target['TRANSPORT']} -a {target['IP']} -s {target['PORT']}"
        lib.subproc.sync_run(cmd)

    def ConnectNvme(self, target) -> None:
        for subsys in target["SUBSYSTEMs"]:
            nqn_index = subsys["NQN_INDEX"]
            for i in range(subsys["NUM_SUBSYSTEMS"]):
                nqn = f"{subsys['NQN_PREFIX']}{nqn_index:03d}"
                nqn_index += 1
                cmd = f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no {self.id}@{self.nic_ssh} \
                    sudo nvme connect -n {nqn} -t {target['TRANSPORT']} -a {target['IP']} -s {target['PORT']}"
                lib.subproc.sync_run(cmd)

    def ListNvme(self, target) -> None:
        cmd = f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no {self.id}@{self.nic_ssh} \
            sudo nvme list"
        device_list = lib.subproc.sync_run(cmd)
        device_lines = device_list.split("\n")
        device_num = len(device_lines)
        find_device = False
        for device_idx in range(2, device_num - 1):
            for subsys in target["SUBSYSTEMs"]:
                sn_index = subsys["SN_INDEX"]
                find_device = False
                for i in range(subsys["NUM_SUBSYSTEMS"]):
                    sn = f"{subsys['SN_PREFIX']}{sn_index:03d}"
                    sn_index += 1
                    if sn in device_lines[device_idx]:
                        device_node = device_lines[device_idx].split(" ")[0]
                        self.device_list.append(device_node)
                        find_device = True
                        break
                if (find_device):
                    break
        print(" KDD Dev List:", self.device_list)

    def GetVolumeIdOfDevice(self, device_list):
        volume_id_list = {}
        for key in device_list:
            cmd = f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no {self.id}@{self.nic_ssh} \
                sudo nvme list | awk '{{if ($1 == \"{key}\") print $2}}'"
            serial_number = lib.subproc.sync_run(cmd)
            volId = int(serial_number[3:])
            volume_id_list[key] = volId
        return volume_id_list
