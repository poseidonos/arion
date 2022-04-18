import graph.draw
import graph.fio_parser
import lib


class Fio:
    def __init__(self, dir, timestamp, title):
        self.dir = dir
        self.timestamp = timestamp
        self.title = title
        self.file_prefix = f"{dir}/{timestamp}_{title}"
        self.eta_data = {}
        self.result_data = []
        self.result_data.append(
            {"title": "read_iops", "index": [], "value": []})
        self.result_data.append({"title": "read_bw", "index": [], "value": []})
        self.result_data.append(
            {"title": "read_clat_avg", "index": [], "value": []})
        self.result_data.append(
            {"title": "read_clat_99.9th", "index": [], "value": []})
        self.result_data.append(
            {"title": "read_clat_99.99th", "index": [], "value": []})
        self.result_data.append(
            {"title": "read_clat_max", "index": [], "value": []})
        self.result_data.append(
            {"title": "write_iops", "index": [], "value": []})
        self.result_data.append(
            {"title": "write_bw", "index": [], "value": []})
        self.result_data.append(
            {"title": "write_clat_avg", "index": [], "value": []})
        self.result_data.append(
            {"title": "write_clat_99.9th", "index": [], "value": []})
        self.result_data.append(
            {"title": "write_clat_99.99th", "index": [], "value": []})
        self.result_data.append(
            {"title": "write_clat_max", "index": [], "value": []})
        self.log_data = {}
        self.log_data["bw"] = {}
        self.log_data["iops"] = {}
        self.log_data["clat"] = {}

    def copy_data(self, initiator, test_name):
        pw = initiator.pw
        id = initiator.id
        ip = initiator.nic_ssh
        dir = initiator.output_dir
        name = initiator.name
        lib.subproc.sync_run(
            f"sshpass -p {pw} scp {id}@{ip}:{dir}/{self.timestamp}_{test_name}_{name} {self.dir}"
        )
        lib.subproc.sync_run(
            f"sshpass -p {pw} scp {id}@{ip}:{dir}/{self.timestamp}_{test_name}_{name}.eta {self.dir}"
        )
        lib.subproc.sync_run(
            f"sshpass -p {pw} scp {id}@{ip}:{dir}/{self.timestamp}_{test_name}_{name}*.log {self.dir}/log"
        )

    def draw_graph(self, initiator, test_name):
        self.add_eta_data(initiator, test_name)
        self.draw_eta(["bw_read", "bw_write", "iops_read", "iops_write"])
        self.add_result_data(initiator, test_name)
        self.draw_result()
        self.add_log_data(initiator, test_name)
        self.draw_log(initiator, test_name)
        self.clear_log_data()

    def add_eta_data(self, initiator, test_name):
        file = f"{self.dir}/{self.timestamp}_{test_name}_{initiator.name}.eta"
        title = f"{test_name}_{initiator.name}"
        graph.fio_parser.GetEtaData(self.eta_data, file, title)

    def draw_eta(self, graph_list):
        graph.draw.DrawEta(self.eta_data, self.file_prefix, graph_list)

    def add_result_data(self, initiator, test_name):
        file = f"{self.dir}/{self.timestamp}_{test_name}_{initiator.name}"
        title = f"{test_name}_{initiator.name}"
        graph.fio_parser.GetResultData(self.result_data, file, title)

    def draw_result(self):
        graph.draw.DrawResult(self.result_data, self.file_prefix)

    def add_log_data(self, initiator, test_name):
        filename = f"{self.timestamp}_{test_name}_{initiator.name}"
        graph.fio_parser.GetLogData(self.log_data, f"{self.dir}/log", filename)

    def draw_log(self, initiator, test_name):
        filepath_name = f"{self.dir}/{self.timestamp}_{test_name}_{initiator.name}"
        graph.draw.DrawLog(self.log_data, filepath_name)

    def clear_log_data(self):
        for data_type in self.log_data:
            for job in self.log_data[data_type]:
                self.log_data[data_type][job]["read"]["x"].clear()
                self.log_data[data_type][job]["read"]["y"].clear()
                self.log_data[data_type][job]["write"]["x"].clear()
                self.log_data[data_type][job]["write"]["y"].clear()
                self.log_data[data_type][job]["read"].clear()
                self.log_data[data_type][job]["write"].clear()
                self.log_data[data_type][job].clear()
            self.log_data[data_type].clear()
        self.log_data.clear()

        self.log_data = {}
        self.log_data["bw"] = {}
        self.log_data["iops"] = {}
        self.log_data["clat"] = {}
