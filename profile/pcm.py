from typing import Dict, List
import csv
import graph.draw
import lib
import node.node
import node.target
import node.initiator
import re


def start(node: node.node.Node, test_name: str, timestamp: str, interval: int) -> None:
    """ If node has PCM setting, run pcm.

    Args:
        node (node.node.Node): Node object.
        test_name (str): Will be included in output file name.
        timestamp (str): Will be included in output file name.
        interval (int): Will be used for PCM's interval option.
    """
    if node.json.get("PROFILE") and node.json["PROFILE"].get("PCM"):
        pcm_dir = node.json["PROFILE"]["PCM"]["BIN_DIR"]
        node.async_run((
            f"{pcm_dir}/pcm-memory {interval} "
            f"-csv={pcm_dir}/{timestamp}_{test_name}_{node.name}_pcm_memory.csv"
        ), True)
        node.async_run((
            f"{pcm_dir}/pcm {interval} "
            f"-csv={pcm_dir}/{timestamp}_{test_name}_{node.name}_pcm_cpu.csv"
        ), True)


def end(node: node.node.Node, test_name: str, timestamp: str, output_dir: str) -> None:
    """ Stop profiling, Copy result and Draw graphs.

    Args:
        node (node.node.Node): Node object.
        test_name (str): Will be included in output file name.
        timestamp (str): Will be included in output file name.
        output_dir (str): Directory for profiled raw data.
    """
    if node.json.get("PROFILE") and node.json["PROFILE"].get("PCM"):
        pcm_dir = node.json["PROFILE"]["PCM"]["BIN_DIR"]
        node.sync_run("pkill -9 pcm")
        node.sync_run("pkill -9 pcm-memory")
        lib.subproc.sync_run((
            f"sshpass -p {node.pw} scp {node.id}@{node.nic_ssh}"
            f":{pcm_dir}/*.csv {output_dir}/profile"
        ))
        node.sync_run(f"rm {pcm_dir}/*.csv")
        pcm_memory_csv = f"{output_dir}/profile/{timestamp}_{test_name}_{node.name}_pcm_memory.csv"
        pcm_memory_png = f"{output_dir}/{timestamp}_{test_name}_{node.name}_pcm_memory.png"
        draw_pcm_memory_graph(pcm_memory_csv, pcm_memory_png)
        pcm_cpu_csv = f"{output_dir}/profile/{timestamp}_{test_name}_{node.name}_pcm_cpu.csv"
        pcm_cpu_png = f"{output_dir}/{timestamp}_{test_name}_{node.name}_pcm_cpu.png"
        draw_pcm_cpu_graph(pcm_cpu_csv, pcm_cpu_png)


def draw_pcm_memory_graph(raw_csv_file: str, graph_png_file: str) -> None:
    """ Parse raw data to graphable data and call draw function.

    Args:
        raw_csv_file (str): Raw csv file with path.
        graph_png_file (str): PNG file name with path. This file will be created if success.
    """
    with open(raw_csv_file, "r", encoding="utf-8") as file:
        tsd: Dict[str, List[str]] = {}  # time series data
        title_prefix: List[str] = []
        reader = csv.reader(file)
        len_row = 0
        for idx, row in enumerate(reader):
            if 0 == idx:
                title_prefix = row
                len_row = len(row)
            elif 1 == idx:
                for idx_suffix, suffix in enumerate(row):
                    tsd[title_prefix[idx_suffix] + suffix] = []
            elif len_row == len(row):
                for idx_tsd, key_tsd in enumerate(tsd):
                    if len(row) > idx_tsd:
                        tsd[key_tsd].append(row[idx_tsd])

        tsd_system = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                      if "System" in key and "PMM" not in key and "DRAM" not in key}
        tsd_skts = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                    if "SKT" in key and "Mem" in key}
        tsd_skt0 = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                    if "SKT0" in key and "Ch" in key and "PMM" not in key}
        tsd_skt1 = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                    if "SKT1" in key and "Ch" in key and "PMM" not in key}
        for idx, value in enumerate(tsd["Date"]):
            tsd["Time"][idx] = value + " " + tsd["Time"][idx]

        graph.draw.DrawPcmMemoryGraphs(graph_png_file, tsd["Time"], {
            "System": tsd_system,
            "SKTs": tsd_skts,
            "SKT0": tsd_skt0,
            "SKT1": tsd_skt1
        })


def draw_pcm_cpu_graph(raw_csv_file: str, graph_png_file: str) -> None:
    """ Parse raw data to graphable data and call draw function.

    Args:
        raw_csv_file (str): Raw csv file with path.
        graph_png_file (str): PNG file name with path. This file will be created if success.
    """
    with open(raw_csv_file, "r", encoding="utf-8") as file:
        tsd: Dict[str, List[str]] = {}  # time series data
        title_prefix: List[str] = []
        reader = csv.reader(file)
        len_row = 0
        for idx, row in enumerate(reader):
            if 0 == idx:
                # title_prefix = row
                last_row_val = ""
                for val_row in row:
                    if "" == val_row:
                        title_prefix.append(last_row_val)
                    else:
                        last_row_val = val_row
                        title_prefix.append(val_row)
                len_row = len(row)
            elif 1 == idx:
                for idx_suffix, suffix in enumerate(row):
                    tsd[title_prefix[idx_suffix] + suffix] = []
            elif len_row == len(row):
                for idx_tsd, key_tsd in enumerate(tsd):
                    if len(row) > idx_tsd:
                        tsd[key_tsd].append(row[idx_tsd])

        for idx, value in enumerate(tsd["SystemDate"]):
            tsd["SystemTime"][idx] = value + " " + tsd["SystemTime"][idx]

        y_vals: Dict[str, Dict[str, List[float]]] = {}

        tsd_system = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                      if "SystemEXEC" in key or "SystemIPC" in key or "SystemFREQ" in key
                      or "SystemAFREQ" in key or "SystemL3HIT" in key or "SystemL2HIT" in key
                      or "SystemL3MPI" in key or "SystemL2MPI" in key}
        y_vals["System"] = tsd_system

        tsd_system_cm = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                         if "SystemL3MISS" in key or "SystemL2MISS" in key}
        y_vals["System Cache Miss"] = tsd_system_cm

        tsd_skts = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                    if re.search("^Socket [0-9]*", key) and "Phys" not in key and
                    ("IPC" in key or "L3HIT" in key or "L2HIT" in key or "L3MPI" in key or
                    "L2MPI" in key)}
        y_vals["Sockets"] = tsd_skts

        tsd_skts_etc = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                        if re.search("^Socket [0-9]*", key) and "Phys" not in key and
                        ("L3MISS" in key or "L2MISS" in key or "LMB" in key or "RMB" in key)}
        y_vals["Sockets Etc"] = tsd_skts_etc

        tsd_system_upi = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                          if re.search("^SystemTotalUPI*", key)}
        y_vals["System UPI"] = tsd_system_upi

        tsd_skts_upi = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                        if re.search("^SKT[0-9](dataIn|trafficOut)UPI*", key) and "percent" not in key}
        y_vals["Sockets UPI"] = tsd_skts_upi

        core_idx = 0
        while True:
            start_core = core_idx * 10
            end_core = start_core + 9
            miss_title = f"Cores {start_core}-{end_core} MISS"
            hit_title = f"Cores {start_core}-{end_core} HIT"
            regex_core = ""
            if 0 == core_idx:
                regex_core = "^Core[0-9] (Socket [0-3])*"
            else:
                regex_core = f"^Core{core_idx}[0-9] (Socket [0-3])*"
            tsd_core_miss = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                             if re.search(regex_core, key) and
                             ("L3MISS" in key or "L2MISS" in key)}
            if 0 == len(tsd_core_miss):
                break
            y_vals[miss_title] = tsd_core_miss

            tsd_core_hit = {key: [float(val) for val in str_list] for key, str_list in tsd.items()
                            if re.search(regex_core, key) and
                            ("L3HIT" in key or "L2HIT" in key)}
            y_vals[hit_title] = tsd_core_hit
            core_idx += 1

        graph.draw.DrawPcmCpuGraphs(graph_png_file, tsd["SystemTime"], y_vals)
