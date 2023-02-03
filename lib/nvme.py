import json
import lib


class Cli:
    def __init__(self, json):
        self.prefix = (
            f"sshpass -p {json['PW']} ssh -o StrictHostKeyChecking=no"
            f" {json['ID']}@{json['NIC']['SSH']} sudo"
        )

    def _send_cli(self, cmd, fmt="normal", ignore_err=False):
        if fmt == "json":
            return lib.parser.parse_str_to_dict(lib.subproc.sync_run(f"{self.prefix} {cmd}"), ignore_err)
        else:
            return lib.subproc.sync_run(f"{self.prefix} {cmd}")

    def connect(self, nqn, transport, traddr, trsvcid, fmt="normal"):
        return self._send_cli(f"nvme connect -n {nqn} -t {transport} -a {traddr} -s {trsvcid}", fmt)

    def copy(self, device, sdlba, slbs, blocks, format=0):
        return self._send_cli(f"nvme copy {device} -d {sdlba} -s {slbs} -b {blocks} -F {format}")

    def disconnect_device(self, device):
        return self._send_cli(f"nvme disconnect -d {device}")

    def disconnect_nqn(self, nqn):
        return self._send_cli(f"nvme disconnect -n {nqn}")

    def discover(self, transport, traddr, trsvcid, fmt="normal"):
        return self._send_cli(f"nvme discover -t {transport} -a {traddr} -s {trsvcid}", fmt)

    def id_ctrl(self, device, fmt="normal"):
        return self._send_cli(f"nvme id-ctrl {device} -o {fmt}", fmt)

    def id_ns(self, device, fmt="normal"):
        return self._send_cli(f"nvme id-ns {device} -o {fmt}", fmt)

    def list(self, fmt="normal"):
        return self._send_cli(f"nvme list -o {fmt}", fmt, True)

    def zns_close_zone(self, device, slba, all):
        if all:
            return self._send_cli(f"nvme zns close-zone {device} -a")
        else:
            return self._send_cli(f"nvme zns close-zone {device} -s {slba}")

    def zns_finish_zone(self, device, slba, all):
        if all:
            return self._send_cli(f"nvme zns finish-zone {device} -a")
        else:
            return self._send_cli(f"nvme zns finish-zone {device} -s {slba}")

    def zns_id_ctrl(self, device, fmt="normal"):
        return self._send_cli(f"nvme zns id-ctrl {device} -o {fmt}", fmt)

    def zns_id_ns(self, device, fmt="normal"):
        return self._send_cli(f"nvme zns id-ns {device} -o {fmt}", fmt)

    def zns_offline_zone(self, device, slba, all):
        if all:
            return self._send_cli(f"nvme zns offline-zone {device} -a")
        else:
            return self._send_cli(f"nvme zns offline-zone {device} -s {slba}")

    def zns_open_zone(self, device, slba, all):
        if all:
            return self._send_cli(f"nvme zns open-zone {device} -a")
        else:
            return self._send_cli(f"nvme zns open-zone {device} -s {slba}")

    def zns_report_zones(self, device, state, partial=False, fmt="normal"):
        if partial:
            return self._send_cli(f"nvme zns report-zones {device} -S {state} -p -o {fmt}", fmt)
        else:
            return self._send_cli(f"nvme zns report-zones {device} -S {state} -o {fmt}", fmt)

    def zns_reset_zone(self, device, slba, all):
        if all:
            return self._send_cli(f"nvme zns reset-zone {device} -a")
        else:
            return self._send_cli(f"nvme zns reset-zone {device} -s {slba}")

    def zns_zone_mgmt_recv(self, device, zra, partial=False, fmt="normal"):
        if partial:
            return self._send_cli(f"nvme zns zone-mgmt-recv {device} -z {zra} -p -o {fmt}", fmt)
        else:
            return self._send_cli(f"nvme zns zone-mgmt-recv {device} -z {zra} -o {fmt}", fmt)

    def zns_zone_mgmt_send(self, deivce, slba, all, zsa, data, data_len):
        if zsa == 16:
            return self._send_cli(f"nvme zns zone-mgmt-send {device} -s {slba} -z {zsa} -d {data} -l {data_len}")
        elif all:
            return self._send_cli(f"nvme zns zone-mgmt-send {device} -a -z {zsa}")
        else:
            return self._send_cli(f"nvme zns zone-mgmt-send {device} -s {slba} -z {zsa}")
