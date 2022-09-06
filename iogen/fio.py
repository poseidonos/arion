from packaging import version

import lib
import node


class Fio:
    def __init__(self, initiator: node.initiator.Initiator, timestamp: str) -> None:
        """ Initialize Fio object with initiator data.

        Args:
            initiator (node.initiator.Initiator): Read some initiator info.
            timestamp (str): Will be included in output file name.
        """
        self.initiator = initiator
        self.version = initiator.fio_version[4:].split("-")[0]
        self.opt = {}
        self.jobs = []
        self.linked_jobs = []
        self.kdd_mode = False
        self.timestamp = timestamp

    def initialize(self, kdd_mode: bool = False) -> None:
        """ Set FIO default options.

        Args:
            kdd_mode (bool, optional): If True, FIO uses kernel library. Defaults to False.
        """
        self.kdd_mode = kdd_mode
        self.jobs.clear()
        self.linked_jobs.clear()
        self.opt.clear()
        self.opt["numjobs"] = "1"
        self.opt["thread"] = "1"
        if (self.kdd_mode):
            self.opt["ioengine"] = "libaio"
            self.add_kdd_jobs()
        else:
            self.opt["ioengine"] = f"{self.initiator.spdk_dir}/examples/nvme/fio_plugin/fio_plugin"
            self.add_udd_jobs()

        self.opt["direct"] = "1"
        self.opt["rw"] = "write"
        self.opt["norandommap"] = "1"
        self.opt["bs"] = "4k"
        self.opt["iodepth"] = "32"
        self.opt["size"] = "100%"
        self.opt["io_size"] = "100%"
        self.opt["serialize_overlap"] = "1"
        self.opt["verify"] = "0"

        self.opt["ramp_time"] = "0"
        self.opt["runtime"] = "0"
        self.opt["time_based"] = "0"

        self.opt["eta"] = "always"
        if (version.parse(self.version) >= version.parse("3.3")):
            self.opt["eta-interval"] = "2"
        self.opt["group_reporting"] = "1"
        self.opt["output-format"] = "json"
        self.opt["per_job_logs"] = "1"
        self.opt["log_unix_epoch"] = "1"
        self.opt["log_avg_msec"] = "2000"

    def update(self, test_case: dict, job_list: list = []) -> None:
        """ Update test_case specific FIO options.

        Args:
            test_case (dict): key is a FIO option, value type has to be string type
            job_list (list, optional): If set like [1, 3], connect 1st & 3rd job(subsystem)s among subsystems defined in this initiator's config. Defaults to [] (connect all).
        """
        self.opt["output"] = f"{self.initiator.output_dir}/{self.timestamp}_{test_case['name']}_{self.initiator.name}"
        self.opt["write_bw_log"] = self.opt["output"]
        self.opt["write_iops_log"] = self.opt["output"]
        self.opt["write_lat_log"] = self.opt["output"]
        for key in test_case:
            if key != "name":
                if key == "eta-interval" and version.parse(self.version) < version.parse("3.3"):
                    lib.printer.red((
                        f"eta-interval option can be supported 3.3 or higher\n"
                        f"current initiator's fio version: {self.version}"
                    ))
                    continue
                self.opt[key] = test_case[key]
        if (self.opt["verify"] != "0"):
            self.opt["norandommap"] = "0"
            self.opt["serialize_overlap"] = "0"
        self.linked_jobs = job_list

    def stringify(self) -> str:
        """ Stringify FIO options

        Returns:
            str: fio run command
        """
        str = f"sshpass -p {self.initiator.pw} ssh {self.initiator.id}@{self.initiator.nic_ssh} nohup 'fio"
        for key in self.opt:
            str += f" --{key}={self.opt[key]}"
        if 0 == len(self.linked_jobs):
            for job in self.jobs:
                str += job
        else:
            for index in self.linked_jobs:
                str += self.jobs[index - 1]
        str += f" > {self.opt['output']}.eta"
        str += "'"
        return str

    def add_kdd_jobs(self):
        for device in self.initiator.device_list:
            self.jobs.append(f" --name=job_{device} --filename={device}")

    def add_udd_jobs(self):
        for tgt in self.initiator.targets:
            for subsys in tgt["SUBSYSTEMs"]:
                nqn_index = subsys["NQN_INDEX"]
                for subsys_idx in range(subsys["NUM_SUBSYSTEMS"]):
                    nqn = f"{subsys['NQN_PREFIX']}{nqn_index:03d}"
                    ns = subsys["NS_INDEX"]
                    for ns_idx in range(subsys["NUM_NS"]):
                        self.jobs.append(
                            (
                                f" --name=job_{tgt['NAME']}_{nqn}_{ns}"
                                f" --filename=\"trtype={tgt['TRANSPORT']}"
                                f" adrfam=IPv4 traddr={tgt['IP']}"
                                f" trsvcid={tgt['PORT']} subnqn={nqn} ns={ns}\""
                            )
                        )
                        ns += 1
                    nqn_index += 1

    def get_interval(self) -> int:
        if self.opt.get("eta-interval"):
            return int(self.opt["eta-interval"])
        else:
            return 1
