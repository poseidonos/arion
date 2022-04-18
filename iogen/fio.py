import asyncio
import copy
import lib


class Fio:
    def __init__(self, initiator, timestamp):
        self.initiator = initiator
        self.opt = {}
        self.jobs = []
        self.kdd_mode = False
        self.timestamp = timestamp

    def initialize(self, kdd_mode=False):
        self.kdd_mode = kdd_mode
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
        self.opt["group_reporting"] = "1"
        self.opt["output-format"] = "json"
        self.opt["per_job_logs"] = "1"
        self.opt["log_unix_epoch"] = "1"
        self.opt["log_avg_msec"] = "1000"

    def update(self, test_case):
        self.opt["output"] = f"{self.initiator.output_dir}/{self.timestamp}_{test_case['name']}_{self.initiator.name}"
        self.opt["write_bw_log"] = self.opt["output"]
        self.opt["write_iops_log"] = self.opt["output"]
        self.opt["write_lat_log"] = self.opt["output"]
        for key in test_case:
            if key != "name":
                self.opt[key] = test_case[key]
        if (self.opt["verify"] != "0"):
            if "-" in self.opt["bs"] and self.opt["norandommap"] != "0":
                self.opt["norandommap"] = "0"

    def stringify(self):
        str = f"sshpass -p {self.initiator.pw} ssh {self.initiator.id}@{self.initiator.nic_ssh} nohup 'fio"
        for key in self.opt:
            str += f" --{key}={self.opt[key]}"
        for job in self.jobs:
            str += job
        str += f" > {self.opt['output']}.eta"
        str += "'"
        return str

    def add_kdd_jobs(self):
        return

    def add_udd_jobs(self):
        for tgt in self.initiator.targets:
            for subsys in tgt["SUBSYSTEMs"]:
                nqn_index = subsys["NQN_INDEX"]
                for subsys_idx in range(subsys["NUM_SUBSYSTEMS"]):
                    nqn = f"{subsys['NQN_PREFIX']}{nqn_index:03d}"
                    ns = subsys["NS_INDEX"]
                    for ns_idx in range(subsys["NUM_NS"]):
                        self.jobs.append(
                            f" --name=job_{tgt['NAME']}_{nqn}_{ns} --filename=\"trtype={tgt['TRANSPORT']} \
                                adrfam=IPv4 traddr={tgt['IP']} trsvcid={tgt['PORT']} subnqn={nqn} ns={ns}\""
                        )
                        ns += 1
                    nqn_index += 1
