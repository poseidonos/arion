from node import node
import json
import lib
import pos
import prerequisite
import time


class Target(node.Node):
    def __init__(self, json):
        self.json = json
        self.name = json["NAME"]
        self.id = json["ID"]
        self.pw = json["PW"]
        self.nic_ssh = json["NIC"]["SSH"]
        self.spdk_dir = json["POS"]["DIR"] + "/lib/spdk"
        self.pos_tp = json["POS"]["TRANSPORT"]["TYPE"]
        self.pos_tp_num_shd_buf = json["POS"]["TRANSPORT"]["NUM_SHARED_BUFFER"]
        self.pos_dir = json["POS"]["DIR"]
        self.pos_bin = json["POS"]["BIN"]
        self.pos_cfg = json["POS"]["CFG"]
        try:
            self.pos_wait = json["POS"]["WAIT_AFTER_EXE"]
        except Exception as e:
            self.pos_wait = 15
        try:
            self.pos_log = json["POS"]["LOG"]
        except Exception as e:
            self.pos_log = ""
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
        try:
            self.asan_opt = json["POS"]["ASAN_OPTIONS"]
        except Exception as e:
            self.asan_opt = ""
        self.cli = pos.cli.Cli(json, self.cli_local_run)
        self.prereq_manager = prerequisite.manager.Manager(json, self.spdk_dir)
        self.cmd_prefix = (
            f"sshpass -p {self.pw} ssh -o StrictHostKeyChecking=no "
            f"{self.id}@{self.nic_ssh} sudo nohup "
        )

    def bring_up(self) -> None:
        lib.printer.green(f" {__name__}.bring_up start : {self.name}")

        # Step 1. Prerequisite Setting
        self.prereq_manager.run()

        # Step 2. POS Running
        result = pos.env.is_pos_running(
            self.id, self.pw, self.nic_ssh, self.pos_bin)
        if (result):
            pos.env.kill_pos(self.id, self.pw, self.nic_ssh, self.pos_bin)
            time.sleep(1)
        pos.env.copy_pos_config(
            self.id, self.pw, self.nic_ssh, self.pos_dir, self.pos_cfg)
        self.pos_exe_thread = pos.env.execute_pos(
            self.id, self.pw, self.nic_ssh,
            self.pos_bin, self.pos_dir, self.pos_log, self.asan_opt)

        lib.printer.yellow(
            f"wait for {self.pos_wait} seconds until POS ready to handle CLI")
        time.sleep(self.pos_wait)

        if (False == self.pos_exe_thread.is_alive()):
            self.pos_exe_thread.join()
            raise Exception("POS terminated abnormally.")

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
                    nqn, self.pos_tp, subsys["IP"], subsys["PORT"])

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
                    max_iops = 0
                    max_bw = 0
                    if vol.get("MAX_IOPS"):
                        max_iops = vol["MAX_IOPS"]
                    if vol.get("MAX_BW"):
                        max_bw = vol["MAX_BW"]
                    self.cli.volume_create(
                        name, size, arr["NAME"], max_iops, max_bw)
                    self.cli.volume_mount(name, nqn, arr["NAME"])

        json_obj = json.loads(self.cli.subsystem_list())
        print(json.dumps(json_obj, indent=2))
        lib.printer.green(f" {__name__}.bring_up end : {self.name}")

    def wrap_up(self) -> None:
        for array in self.json["POS"]["ARRAYs"]:
            self.cli.array_unmount(array["NAME"])
        self.cli.system_stop()
        self.pos_exe_thread.join()
        lib.printer.green(f" {__name__}.wrapp_up end : {self.name}")

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

    def forced_exit(self) -> None:
        pos.env.kill_pos(self.id, self.pw, self.nic_ssh, self.pos_bin)
        time.sleep(1)
        lib.printer.green(f" {__name__}.forced_exit end : {self.name}")

    def forced_dump(self) -> None:
        pos.env.dump_pos(self.id, self.pw, self.nic_ssh, self.pos_bin)
        time.sleep(1)
        lib.printer.green(f" {__name__}.forced_dump end : {self.name}")

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
