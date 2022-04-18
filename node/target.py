import json
import lib
import os
import pos
import prerequisite
import time


class Target:
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
        self.spdk_dir = json["POS"]["DIR"] + "/lib/spdk"
        self.pos_tp = json["POS"]["TRANSPORT"]["TYPE"]
        self.pos_tp_num_shd_buf = json["POS"]["TRANSPORT"]["NUM_SHARED_BUFFER"]
        self.pos_dir = json["POS"]["DIR"]
        self.pos_bin = json["POS"]["BIN"]
        self.pos_cfg = json["POS"]["CFG"]
        self.pos_log = json["POS"]["LOG"]
        try:
            self.pos_dirty_bringup = json["POS"]["DIRTY_BRINGUP"]
        except Exception as e:
            self.pos_dirty_bringup = False
        try:
            self.pos_logger_level = json["POS"]["LOGGER_LEVEL"]
        except Exception as e:
            self.pos_logger_level = "info"
        try:
            self.pos_telemetry = json["POS"]["TELEMETRY"]
        except Exception as e:
            self.pos_telemetry = True
        try:
            self.cli_local_run = json["POS"]["CLI_LOCAL_RUN"]
        except Exception as e:
            self.cli_local_run = False
        self.cli = pos.cli.Cli(json, self.cli_local_run)

    def bring_up(self) -> None:
        lib.printer.green(f" {__name__}.bring_up start : {self.name}")

        # Step 1. Prerequisite Setting
        if (self.prereq and self.prereq["CPU"]["RUN"]):
            prerequisite.cpu.Scaling(
                self.id, self.pw, self.nic_ssh, self.prereq["CPU"]["SCALING"])
        if (self.prereq and self.prereq["SSD"]["RUN"]):
            prerequisite.ssd.Format(self.id, self.pw, self.nic_ssh, self.prereq["SSD"]["FORMAT"],
                                    self.prereq["SSD"]["UDEV_FILE"], self.spdk_dir, self.pos_dir)
        if (self.prereq and self.prereq["MEMORY"]["RUN"]):
            prerequisite.memory.MaxMapCount(
                self.id, self.pw, self.nic_ssh, self.prereq["MEMORY"]["MAX_MAP_COUNT"])
            prerequisite.memory.DropCaches(
                self.id, self.pw, self.nic_ssh, self.prereq["MEMORY"]["DROP_CACHES"])
        if (self.prereq and self.prereq["NETWORK"]["RUN"]):
            prerequisite.network.IrqBalance(
                self.id, self.pw, self.nic_ssh, self.prereq["NETWORK"]["IRQ_BALANCE"])
            prerequisite.network.TcpTune(
                self.id, self.pw, self.nic_ssh, self.prereq["NETWORK"]["TCP_TUNE"])
            prerequisite.network.IrqAffinity(self.id, self.pw, self.nic_ssh,
                                             self.prereq["NETWORK"]["IRQ_AFFINITYs"],
                                             self.pos_dir)
            prerequisite.network.Nic(
                self.id, self.pw, self.nic_ssh, self.prereq["NETWORK"]["NICs"])
        if (self.prereq and self.prereq["MODPROBE"]["RUN"]):
            prerequisite.modprobe.Modprobe(
                self.id, self.pw, self.nic_ssh, self.prereq["MODPROBE"]["MODs"])
        if (self.prereq and self.prereq["SPDK"]["RUN"]):
            prerequisite.spdk.Setup(
                self.id, self.pw, self.nic_ssh, self.prereq["SPDK"], self.spdk_dir)
        if (self.prereq and self.prereq["DEBUG"]["RUN"]):
            prerequisite.debug.Ulimit(
                self.id, self.pw, self.nic_ssh, self.prereq["DEBUG"]["ULIMIT"])
            prerequisite.debug.Apport(
                self.id, self.pw, self.nic_ssh, self.prereq["DEBUG"]["APPORT"])
            prerequisite.debug.CorePattern(self.id, self.pw, self.nic_ssh,
                                           self.prereq["DEBUG"]["DUMP_DIR"],
                                           self.prereq["DEBUG"]["CORE_PATTERN"])

        # Step 2. POS Running
        result = pos.env.is_pos_running(
            self.id, self.pw, self.nic_ssh, self.pos_bin)
        if (result):
            pos.env.kill_pos(self.id, self.pw, self.nic_ssh, self.pos_bin)
            time.sleep(1)
        pos.env.copy_pos_config(
            self.id, self.pw, self.nic_ssh, self.pos_dir, self.pos_cfg)
        pos.env.execute_pos(self.id, self.pw, self.nic_ssh,
                            self.pos_bin, self.pos_dir, self.pos_log)
        time.sleep(5)

        # Step 3. POS Setting
        self.cli.subsystem_create_transport(
            self.pos_tp, self.pos_tp_num_shd_buf)
        self.cli.logger_set_level(self.pos_logger_level)
        if (self.pos_telemetry):
            self.cli.telemetry_start()
        else:
            self.cli.telemetry_stop()

        # Step 3.1. subsystem create, add listener
        for subsys in self.json["POS"]["SUBSYSTEMs"]:
            nqn_index = subsys["NQN_INDEX"]
            sn_index = subsys["SN_INDEX"]
            for i in range(subsys["NUM_SUBSYSTEMS"]):
                nqn = f"{subsys['NQN_PREFIX']}{nqn_index:03d}"
                sn = f"{subsys['SN_PREFIX']}{sn_index:03d}"
                nqn_index += 1
                sn_index += 1
                self.cli.subsystem_create(nqn, sn)
                self.cli.subsystem_add_listener(
                    nqn, self.pos_tp, self.json["NIC"][subsys["IP"]], subsys["PORT"])

        # Step 3.2. device create, scan, list
        for dev in self.json["POS"]["DEVICEs"]:
            self.cli.device_create(
                dev["NAME"], dev["TYPE"], dev["NUM_BLOCKS"], dev["BLOCK_SIZE"], dev["NUMA"])
        self.cli.device_scan()
        json_obj = json.loads(self.cli.device_list())
        print(json.dumps(json_obj, indent=2))

        if (self.pos_dirty_bringup):
            self.dirty_bring_up()
            return

        # Step 3.3. array reset, create, mount
        self.cli.array_reset()
        for arr in self.json["POS"]["ARRAYs"]:
            self.cli.array_create(
                arr["BUFFER_DEV"],
                arr["USER_DEVICE_LIST"],
                arr["SPARE_DEVICE_LIST"],
                arr["NAME"],
                arr["RAID_OR_MEDIA"]
            )
            if arr.get("WRITE_THROUGH"):
                self.cli.array_mount(arr["NAME"], arr["WRITE_THROUGH"])
            else:
                self.cli.array_mount(arr["NAME"])
            json_obj = json.loads(self.cli.array_list(arr["NAME"]))
            print(json.dumps(json_obj, indent=2))

        # Step 3.4. volume create, mount
        for arr in self.json["POS"]["ARRAYs"]:
            for vol in arr["VOLUMEs"]:
                name_index = vol["NAME_INDEX"]
                nqn_index = vol["NQN_INDEX"]
                for i in range(vol["NUM_VOLUMES"]):
                    name = f"{vol['NAME_PREFIX']}{name_index:03d}"
                    nqn = f"{vol['NQN_PREFIX']}{nqn_index:03d}"
                    name_index += 1
                    nqn_index += 1
                    if (nqn_index >= vol["NQN_INDEX"] + vol["USE_SUBSYSTEMS"]):
                        nqn_index = vol["NQN_INDEX"]
                    size = vol["SIZE_MiB"] * 1048576
                    self.cli.volume_create(name, size, arr["NAME"])
                    self.cli.volume_mount(name, nqn, arr["NAME"])

        json_obj = json.loads(self.cli.subsystem_list())
        print(json.dumps(json_obj, indent=2))
        lib.printer.green(f" {__name__}.bring_up end : {self.name}")

    def wrap_up(self) -> None:
        for array in self.json["POS"]["ARRAYs"]:
            self.cli.array_unmount(array["NAME"])
        self.cli.system_stop()
        lib.printer.green(f" {__name__}.wrapp_up end : {self.name}")

    def forced_exit(self) -> None:
        pos.env.kill_pos(self.id, self.pw, self.nic_ssh, self.pos_bin)
        time.sleep(1)
        lib.printer.green(f" {__name__}.forced_exit end : {self.name}")

    def dirty_bring_up(self) -> None:
        # Step 3.3. array mount
        for arr in self.json["POS"]["ARRAYs"]:
            if arr.get("WRITE_THROUGH"):
                self.cli.array_mount(arr["NAME"], arr["WRITE_THROUGH"])
            else:
                self.cli.array_mount(arr["NAME"])
            json_obj = json.loads(self.cli.array_list(arr["NAME"]))
            print(json.dumps(json_obj, indent=2))

        # Step 3.4. volume mount
        for arr in self.json["POS"]["ARRAYs"]:
            for vol in arr["VOLUMEs"]:
                name_index = vol["NAME_INDEX"]
                nqn_index = vol["NQN_INDEX"]
                for i in range(vol["NUM_VOLUMES"]):
                    name = f"{vol['NAME_PREFIX']}{name_index:03d}"
                    nqn = f"{vol['NQN_PREFIX']}{nqn_index:03d}"
                    name_index += 1
                    nqn_index += 1
                    if (nqn_index >= vol["NQN_INDEX"] + vol["USE_SUBSYSTEMS"]):
                        nqn_index = vol["NQN_INDEX"]
                    self.cli.volume_mount(name, nqn, arr["NAME"])

        json_obj = json.loads(self.cli.subsystem_list())
        print(json.dumps(json_obj, indent=2))
        lib.printer.green(f" {__name__}.dirty_bring_up end : {self.name}")

    def detach_device(self, dev) -> None:
        return pos.env.detach_device(self.id, self.pw, self.nic_ssh, dev)

    def pcie_scan(self) -> None:
        return pos.env.pcie_scan(self.id, self.pw, self.nic_ssh)

    def check_rebuild_complete(self, arr_name):
        return self.cli.array_list(arr_name)

    def device_list(self):
        return self.cli.device_list()

    def add_spare(self, arr_name, dev_name):
        return self.cli.array_add_spare(arr_name, dev_name)

    def set_rebuild_impact(self, impact):
        return self.cli.system_set_property(impact)
