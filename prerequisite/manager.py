import prerequisite.cpu
import prerequisite.debug
import prerequisite.memory
import prerequisite.modprobe
import prerequisite.network
import prerequisite.spdk
import prerequisite.ssd


class Manager:
    def __init__(self, json, spdk_dir):
        self.id = json["ID"]
        self.pw = json["PW"]
        self.ip = json["NIC"]["SSH"]
        self.spdk_dir = spdk_dir
        self.pos_dir = spdk_dir[:len(spdk_dir)-9]
        try:
            self.prereq = json["PREREQUISITE"]
        except Exception as e:
            self.prereq = None

    def run(self):
        if not self.prereq:
            return

        if self.prereq.get("CPU") and self.prereq["CPU"]["RUN"]:
            if self.prereq["CPU"].get("SCALING"):
                prerequisite.cpu.scaling(
                    self.id, self.pw, self.ip, self.prereq["CPU"]["SCALING"]
                )

        if self.prereq.get("SSD") and self.prereq["SSD"]["RUN"]:
            if self.prereq["SSD"].get("FORMAT") and self.prereq["SSD"].get("UDEV_FILE"):
                prerequisite.ssd.format(
                    self.id, self.pw, self.ip, self.prereq["SSD"]["FORMAT"],
                    self.prereq["SSD"]["UDEV_FILE"], self.spdk_dir, self.pos_dir
                )

        if self.prereq.get("MEMORY") and self.prereq["MEMORY"]["RUN"]:
            if self.prereq["MEMORY"].get("MAX_MAP_COUNT"):
                prerequisite.memory.max_map_count(
                    self.id, self.pw, self.ip, self.prereq["MEMORY"]["MAX_MAP_COUNT"]
                )
            if self.prereq["MEMORY"].get("DROP_CACHES"):
                prerequisite.memory.drop_caches(
                    self.id, self.pw, self.ip, self.prereq["MEMORY"]["DROP_CACHES"]
                )

        if self.prereq.get("NETWORK") and self.prereq["NETWORK"]["RUN"]:
            if self.prereq["NETWORK"].get("IRQ_BALANCE"):
                prerequisite.network.irq_balance(
                    self.id, self.pw, self.ip, self.prereq["NETWORK"]["IRQ_BALANCE"]
                )
            if self.prereq["NETWORK"].get("TCP_TUNE"):
                prerequisite.network.tcp_tune(
                    self.id, self.pw, self.ip, self.prereq["NETWORK"]["TCP_TUNE"]
                )
            if self.prereq["NETWORK"].get("IRQ_AFFINITYs"):
                prerequisite.network.irq_affinity(
                    self.id, self.pw, self.ip, self.prereq["NETWORK"]["IRQ_AFFINITYs"],
                    self.pos_dir
                )
            if self.prereq["NETWORK"].get("NICs"):
                prerequisite.network.nic(
                    self.id, self.pw, self.ip, self.prereq["NETWORK"]["NICs"]
                )

        if self.prereq.get("MODPROBE") and self.prereq["MODPROBE"]["RUN"]:
            if self.prereq["MODPROBE"].get("MODs"):
                prerequisite.modprobe.modprobe(
                    self.id, self.pw, self.ip, self.prereq["MODPROBE"]["MODs"]
                )

        if self.prereq.get("SPDK") and self.prereq["SPDK"]["RUN"]:
            if self.prereq["SPDK"].get("HUGE_EVEN_ALLOC") and self.prereq["SPDK"].get("NRHUGE"):
                prerequisite.spdk.setup(
                    self.id, self.pw, self.ip, self.prereq["SPDK"]["HUGE_EVEN_ALLOC"],
                    self.prereq["SPDK"]["NRHUGE"], self.spdk_dir
                )

        if self.prereq.get("DEBUG") and self.prereq["DEBUG"]["RUN"]:
            if self.prereq["DEBUG"].get("ULIMIT"):
                prerequisite.debug.ulimit(
                    self.id, self.pw, self.ip, self.prereq["DEBUG"]["ULIMIT"]
                )
            if self.prereq["DEBUG"].get("APPORT"):
                prerequisite.debug.apport(
                    self.id, self.pw, self.ip, self.prereq["DEBUG"]["APPORT"]
                )
            if self.prereq["DEBUG"].get("DUMP_DIR") and self.prereq["DEBUG"].get("CORE_PATTERN"):
                prerequisite.debug.core_pattern(
                    self.id, self.pw, self.ip, self.prereq["DEBUG"]["DUMP_DIR"],
                    self.prereq["DEBUG"]["CORE_PATTERN"]
                )
