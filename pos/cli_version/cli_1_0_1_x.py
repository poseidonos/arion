import json
import lib
from pos.cli_version import cli_interface


class Cli_1_0_1_x(cli_interface.CliInterface):
    def __init__(self, json, local_run):
        prefix_list = []
        if not local_run:
            prefix_list.append(f"sshpass -p {json['PW']}")
            prefix_list.append(" ssh -o StrictHostKeyChecking=no ")
            prefix_list.append(f"{json['ID']}@{json['NIC']['SSH']}")
            prefix_list.append(" sudo nohup ")

        prefix_list.append(
            f"{json['POS']['DIR']}/bin/{json['POS']['CLI']} --json-res ")
        self.prefix = "".join(prefix_list)

    def _send_cli(self, cmd):
        result = lib.subproc.sync_run(cmd)
        for line in result.splitlines():
            json_obj = json.loads(line)
            if (json_obj["Response"]["result"]["status"]["code"] != 0):
                lib.printer.red(cmd)
                raise Exception(f"{json.dumps(json_obj, indent=2)}")
        return result

    def array_add_spare(self, arr_name, dev_name):
        cli_cmd = self.prefix + f"array addspare -a {arr_name} -s {dev_name}"
        return self._send_cli(cli_cmd)

    def array_create(self, buffer_dev, user_devs, spare_devs, arr_name, media_type):
        cli_cmd = self.prefix + \
            f"array create -d {user_devs} --array-name {arr_name} --media-type {media_type}"
        return self._send_cli(cli_cmd)

    def array_list(self, arr_name):
        cli_cmd = self.prefix + f"array list --array-name {arr_name}"
        return self._send_cli(cli_cmd)

    def array_mount(self, arr_name, wb_mode):
        cli_cmd = self.prefix + f"array mount --array-name {arr_name}"
        if (wb_mode):
            cli_cmd += " -w"
        return self._send_cli(cli_cmd)

    def array_reset(self):
        cli_cmd = self.prefix + f"devel resetmbr"
        return self._send_cli(cli_cmd)

    def array_unmount(self, arr_name):
        cli_cmd = self.prefix + \
            f"array unmount --array-name {arr_name} --force"
        return self._send_cli(cli_cmd)

    def device_create(self, dev_name, dev_type, num_blk, blk_size, numa):
        cli_cmd = self.prefix + \
            f"device create --device-name {dev_name} --device-type {dev_type} --num-blocks {num_blk} --block-size {blk_size} --numa {numa}"
        return self._send_cli(cli_cmd)

    def device_list(self):
        cli_cmd = self.prefix + f"device list"
        return self._send_cli(cli_cmd)

    def device_scan(self):
        cli_cmd = self.prefix + f"device scan"
        return self._send_cli(cli_cmd)

    def logger_apply_filter(self):
        cli_cmd = self.prefix + f"logger apply-filter"
        return self._send_cli(cli_cmd)

    def logger_get_level(self):
        cli_cmd = self.prefix + f"logger get-level"
        return self._send_cli(cli_cmd)

    def logger_info(self):
        cli_cmd = self.prefix + f"logger info"
        return self._send_cli(cli_cmd)

    def logger_set_level(self, level):
        cli_cmd = self.prefix + f"logger set-level --level {level}"
        return self._send_cli(cli_cmd)

    def qos_create(self, arr_name, vol_name, maxbw, maxiops, minbw, miniops):
        cli_cmd = self.prefix + \
            f"qos create --array-name {arr_name} --volume-name {vol_name}"
        if (-1 != maxbw):
            cli_cmd += f" --maxbw {maxbw}"
        if (-1 != maxiops):
            cli_cmd += f" --maxiops {maxiops}"
        if (-1 != minbw):
            cli_cmd += f" --minbw {minbw}"
        if (-1 != miniops):
            cli_cmd += f" --miniops {miniops}"
        return self._send_cli(cli_cmd)

    def qos_reset(self, arr_name, vol_name):
        cli_cmd = self.prefix + \
            f"qos reset --array-name {arr_name} --volume-name {vol_name}"
        return self._send_cli(cli_cmd)

    def subsystem_add_listener(self, nqn, trtype, target_ip, port):
        cli_cmd = self.prefix + \
            f"subsystem add-listener --subnqn {nqn} -t {trtype} -i {target_ip} -p {port}"
        return self._send_cli(cli_cmd)

    def subsystem_create(self, nqn, sn):
        cli_cmd = self.prefix + \
            f"subsystem create --subnqn {nqn} --serial-number {sn} --model-number POS_VOLUME_EXTENSION -m 256 -o"
        return self._send_cli(cli_cmd)

    def subsystem_create_transport(self, trtype, num_shared_buf):
        cli_cmd = self.prefix + \
            f"subsystem create-transport --trtype {trtype} -c 64 --num-shared-buf {num_shared_buf}"
        return self._send_cli(cli_cmd)

    def subsystem_delete(self, nqn):
        cli_cmd = self.prefix + \
            f"subsystem delete --subnqn {nqn} --force"
        return self._send_cli(cli_cmd)

    def subsystem_list(self):
        cli_cmd = self.prefix + f"subsystem list"
        return self._send_cli(cli_cmd)

    def system_info(self):
        cli_cmd = self.prefix + f"system info"
        return self._send_cli(cli_cmd)

    def system_set_property(self, impact):
        cli_cmd = self.prefix + \
            f"system set-property --rebuild-impact {impact}"
        return self._send_cli(cli_cmd)

    def system_stop(self):
        cli_cmd = self.prefix + f"system stop --force"
        return self._send_cli(cli_cmd)

    def telemetry_start(self):
        cli_cmd = self.prefix + f"telemetry start"
        return self._send_cli(cli_cmd)

    def telemetry_stop(self):
        cli_cmd = self.prefix + f"telemetry stop"
        return self._send_cli(cli_cmd)

    def volume_create(self, vol_name, vol_size, arr_name, maxiops, maxbw):
        cli_cmd = self.prefix + \
            f"volume create --volume-name {vol_name} --size {vol_size} --maxiops {maxiops} --maxbw {maxbw} --array-name {arr_name}"
        return self._send_cli(cli_cmd)

    def volume_list(self, arr_name, vol_name):
        cli_cmd = self.prefix + f"volume list --array-name {arr_name}"
        if ("" != vol_name):
            cli_cmd += f" --volume-name {vol_name}"
        return self._send_cli(cli_cmd)

    def volume_mount(self, vol_name, subnqn, arr_name):
        cli_cmd = self.prefix + \
            f"volume mount --volume-name {vol_name} --array-name {arr_name} --subnqn {subnqn} --force"
        return self._send_cli(cli_cmd)

    def nvme_copy(self, dst_array, dst_volume, dst_lba, src_arrays, src_volumes, src_lbas, src_blocks):
        cli_cmd = self.prefix + \
            f"nvme copy --dst-array {dst_array} --dst-volume {dst_volume} --dst-slba {dst_lba} --src-arrays {src_arrays} --src-volumes {src_volumes} --src-lbas {src_lbas} --src-blocks {src_blocks}"
        return self._send_cli(cli_cmd)
