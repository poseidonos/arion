import json
import lib
import os


def to_float(value: str) -> float:
    """ Convert to float.

    Args:
        value (str): Engineering notation.

    Returns:
        float: Converted value.
    """
    if "K" in value or "k" in value:
        return 1000 * float(value[:len(value) - 1])
    if "M" in value or "m" in value:
        return 1000000 * float(value[:len(value) - 1])
    if "G" in value or "g" in value:
        return 1000000000 * float(value[:len(value) - 1])
    return float(value)


def get_eta_data(data: dict, file: str, title: str) -> None:
    """ Get data fram FIO's eta file.

    Args:
        data (dict): Timeseries data will be saved.
        file (str): FIO's eta file path + name.
        title (str): Title of this eta data set will be a title of subplot.
    """
    data[title] = {}  # title이 graph의 subplot 이고 빈 딕셔너리 생성
    data[title]["title"] = title  # subplot 이름 설정
    data[title]["x"] = []  # subplot x 축 빈 리스트 생성
    data[title]["bw_read"] = []  # subplot y 축 (bw_read) 빈 리스트 생성
    data[title]["bw_write"] = []  # subplot y 축 (bw_write) 빈 리스트 생성
    data[title]["iops_read"] = []  # subplot y 축 (iops_read) 빈 리스트 생성
    data[title]["iops_write"] = []  # subplot y 축 (iops_write) 빈 리스트 생성
    fp = open(file, "r")
    lines = fp.readlines()
    for line in lines:
        # Jobs: 3 (f=3): [W(3)][20.8%][r=0KiB/s,w=2027KiB/s][r=0,w=4055 IOPS][eta 00m:19s]
        strings = line.split("[")
        if (6 <= len(strings)):
            percentage = strings[2].split("%")[0]
            if "-" in percentage:
                continue
            bandwidth = strings[3].split(",")
            bw_read = "0"
            bw_write = "0"
            if len(bandwidth) == 2:
                bw_read = bandwidth[0].split("=")[1].split("iB/s")[0]
                bw_write = bandwidth[1].split("=")[1].split("iB/s")[0]
            elif len(bandwidth) == 1:
                if "r=" in bandwidth[0]:
                    bw_read = bandwidth[0].split("=")[1].split("iB/s")[0]
                elif "w=" in bandwidth[0]:
                    bw_write = bandwidth[0].split("=")[1].split("iB/s")[0]
            iops = strings[4].split(",")
            iops_read = "0"
            iops_write = "0"
            if len(iops) == 2:
                iops_read = iops[0].split("=")[1]
                iops_write = iops[1].split("=")[1].split(" ")[0]
            elif len(iops) == 1:
                if "r=" in iops[0]:
                    iops_read = iops[0].split("=")[1].split(" ")[0]
                elif "w=" in iops[0]:
                    iops_write = iops[0].split("=")[1].split(" ")[0]
            data[title]["x"].append(float(percentage))
            data[title]["bw_read"].append(to_float(bw_read))
            data[title]["bw_write"].append(to_float(bw_write))
            data[title]["iops_read"].append(to_float(iops_read))
            data[title]["iops_write"].append(to_float(iops_write))
    fp.close()


def get_result_data(data: dict, file: str, title: str) -> None:
    """ Get data from FIO's result file.

    Args:
        data (dict): Timeseries data will be saved.
        file (str): FIO's result file path + name.
        title (str): Title of this result data set will be a title of subplot.
    """
    for i in range(len(data)):
        data[i]["index"].append(title)  # subplot 이름 설정

    dict_data = lib.parser.parse_json_file(file)
    if not dict_data:
        raise Exception(f"{__name__}")
    else:
        data[0]["value"].append(dict_data["jobs"][0]["read"]["iops"])
        data[1]["value"].append(dict_data["jobs"][0]["read"]["bw"])
        data[2]["value"].append(
            dict_data["jobs"][0]["read"]["clat_ns"]["mean"])
        try:
            data[3]["value"].append(
                dict_data["jobs"][0]["read"]["clat_ns"]["percentile"]["99.900000"])
        except Exception as e:
            data[3]["value"].append(0)
        try:
            data[4]["value"].append(
                dict_data["jobs"][0]["read"]["clat_ns"]["percentile"]["99.990000"])
        except Exception as e:
            data[4]["value"].append(0)
        data[5]["value"].append(
            dict_data["jobs"][0]["read"]["clat_ns"]["max"])
        data[6]["value"].append(dict_data["jobs"][0]["write"]["iops"])
        data[7]["value"].append(dict_data["jobs"][0]["write"]["bw"])
        data[8]["value"].append(
            dict_data["jobs"][0]["write"]["clat_ns"]["mean"])
        try:
            data[9]["value"].append(
                dict_data["jobs"][0]["write"]["clat_ns"]["percentile"]["99.900000"])
        except Exception as e:
            data[9]["value"].append(0)
        try:
            data[10]["value"].append(
                dict_data["jobs"][0]["write"]["clat_ns"]["percentile"]["99.990000"])
        except Exception as e:
            data[10]["value"].append(0)
        data[11]["value"].append(
            dict_data["jobs"][0]["write"]["clat_ns"]["max"])


def get_single_log_file(data, file, index):
    data[index] = {}
    data[index]["read"] = {}
    data[index]["read"]["x"] = []
    data[index]["read"]["y"] = []
    data[index]["write"] = {}
    data[index]["write"]["x"] = []
    data[index]["write"]["y"] = []
    fp = open(file, "r")
    lines = fp.readlines()
    for line in lines:
        line_spliter = line.split(',')
        if (4 <= len(line_spliter)):
            if ("0" in line_spliter[2]):
                data[index]["read"]["x"].append(int(line_spliter[0]))
                data[index]["read"]["y"].append(int(line_spliter[1]))
            elif ("1" in line_spliter[2]):
                data[index]["write"]["x"].append(int(line_spliter[0]))
                data[index]["write"]["y"].append(int(line_spliter[1]))
    fp.close()


def get_log_data(data: dict, dir: str, filename: str) -> None:
    """ Get data from FIO's log file(s).

    Args:
        data (dict): Timeseries data will be saved.
        dir (str): FIO's log file path.
        filename (str): log file name prefix
    """
    bw_file_prefix = f"{filename}_bw"
    iops_file_prefix = f"{filename}_iops"
    clat_file_prefix = f"{filename}_clat"

    files = os.listdir(dir)
    files.sort()
    for file in files:
        if bw_file_prefix in file:
            bw_spliter = file.split('.')
            get_single_log_file(data["bw"], f"{dir}/{file}", bw_spliter[1])
        elif iops_file_prefix in file:
            iops_spliter = file.split('.')
            get_single_log_file(data["iops"], f"{dir}/{file}", iops_spliter[1])
        elif clat_file_prefix in file:
            clat_spliter = file.split('.')
            get_single_log_file(data["clat"], f"{dir}/{file}", clat_spliter[1])
