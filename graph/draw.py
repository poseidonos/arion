import lib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import time


def FormatLatency(value: int, ndigits: int = 1) -> str:
    """ Decorate with latency format (Unit: nano second)

    Args:
        value (int): Round a value to given precision in decimal digits.
        ndigits (int, optional): Precision in decimal digits. Defaults to 1.

    Returns:
        str: Rounded value with latency format
    """
    if value >= 1e9:
        return f"{round(value / 1e9, ndigits)}s"
    elif value >= 1e6:
        return f"{round(value / 1e6, ndigits)}ms"
    elif value >= 1e3:
        return f"{round(value / 1e3, ndigits)}us"
    else:
        return f"{round(value, ndigits)}ns"


def FormatIOPS(value: int, ndigits: int = 1) -> str:
    """ Decorate with IOPS format (Unit: IO/s)

    Args:
        value (int): Round a value to given precision in decimal digits.
        ndigits (int, optional): Precision in decimal digits. Defaults to 1.

    Returns:
        str: Rounded value with IOPS format
    """
    if value >= 1e9:
        return f"{round(value / 1e9, ndigits)}Giops"
    elif value >= 1e6:
        return f"{round(value / 1e6, ndigits)}Miops"
    elif value >= 1e3:
        return f"{round(value / 1e3, ndigits)}Kiops"
    else:
        return f"{round(value, ndigits)}iops"


def FormatBW(value: int, ndigits: int = 1) -> str:
    """ Decorate with bandwidth format (Unit: Byte/s)

    Args:
        value (int): Round a value to given precision in decimal digits.
        ndigits (int, optional): Precision in decimal digits. Defaults to 1.

    Returns:
        str: Rounded value with bandwidth format
    """
    if value >= 1e9:
        return f"{round(value / 1e9, ndigits)}GiB/s"
    elif value >= 1e6:
        return f"{round(value / 1e6, ndigits)}MiB/s"
    elif value >= 1e3:
        return f"{round(value / 1e3, ndigits)}KiB/s"
    else:
        return f"{round(value, ndigits)}B/s"


def FormatKBW(value: int, ndigits: int = 1) -> str:
    """ Decorate with bandwidth format (Unit: Kilo-Byte/s)

    Args:
        value (int): Round a value to given precision in decimal digits.
        ndigits (int, optional): Precision in decimal digits. Defaults to 1.

    Returns:
        str: Rounded value with bandwidth format
    """
    if value >= 1e9:
        return f"{round(value / 1e9, ndigits)}TiB/s"
    elif value >= 1e6:
        return f"{round(value / 1e6, ndigits)}GiB/s"
    elif value >= 1e3:
        return f"{round(value / 1e3, ndigits)}MiB/s"
    else:
        return f"{round(value, ndigits)}KiB/s"


def FormatSimpleFloat(value: int, ndigits: int = 1) -> str:
    """ Omit format.

    Args:
        value (int): Round a value to given precision in decimal digits.
        ndigits (int, optional): Precision in decimal digits. Defaults to 1.

    Returns:
        str: Rounded value with simple prefix format
    """
    if value >= 1e9:
        return f"{round(value / 1e9, ndigits)}"
    elif value >= 1e6:
        return f"{round(value / 1e6, ndigits)}"
    elif value >= 1e3:
        return f"{round(value / 1e3, ndigits)}"
    else:
        return f"{round(value, ndigits)}"


def FormatEpochTime(value: int, ndigits: int = 0) -> str:
    """ Decorate Epoch time to human readable string

    Args:
        value (int): Epoch time.
        ndigits (int, optional): Never used. For funtion argument syntax.

    Returns:
        str: %H:%M:%S
    """
    time_format = time.strftime("%H:%M:%S", time.localtime(value / 1000))
    return time_format


def DrawEta(data: dict, pic_name: str, graph_list: list) -> None:
    """ Draw some graphs based on FIO ETA data on the PNG file.

    Args:
        data (dict): Raw data.
        pic_name (str): PNG file name prefix (pic_name_eta.png).
        graph_list (list): Draw an individual graph at each subplot.
    """
    try:
        plt.clf()  # plot 초기화
        num_graph = len(graph_list)
        # plot size 설정(unit: inch)
        fig = plt.figure(figsize=(8, 3 * num_graph))

        for i in range(num_graph):
            type = graph_list[i]
            ax = plt.subplot(num_graph, 1, i + 1)  # subplot 생성(행, 렬, 순서)
            ax.set_title(type, fontsize=12)
            ax.grid(True, axis="y", color="lightgrey", zorder=0)
            plt.xlabel("percentage", fontsize=9)
            if "iops" in type:
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(FormatIOPS))
            elif "bw" in type:
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(FormatBW))
            else:
                plt.ticklabel_format(axis="y", style="plain")
                ax.yaxis.set_major_formatter(ticker.EngFormatter())
            ax.tick_params(axis='y', labelrotation=30, labelsize=8)
            for v in data.values():
                plt.scatter(v["x"], v[type], s=10,
                            label=v["title"])  # 점 그래프 그리기
                plt.plot(v["x"], v[type])  # 선 그래프 그리기
            plt.legend(fontsize=8, loc="upper left", ncol=2)  # 범례 그리기

        plt.tight_layout()
        plt.savefig(f"{pic_name}_eta.png", dpi=200)
        plt.close(fig)
    except Exception as e:
        lib.printer.red(f"{__name__} [Error] {e}")
        plt.close(fig)


def DrawResult(data: dict, pic_name: str) -> None:
    """ Draw a set of graphs based on FIO result data on the PNG file.

    Args:
        data (dict): Raw data.
        pic_name (str): PNG file name prefix (pic_name_result.png).
    """
    try:
        plt.clf()  # plot 초기화
        fig = plt.figure(figsize=(12, 12))  # plot size 설정(unit: inch)
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        color_list = prop_cycle.by_key()["color"]

        for i in range(12):
            ax = plt.subplot(4, 3, i + 1)  # subplot 생성(행, 렬, 순서)
            ax.set_title(data[i]["title"], fontsize=12)
            ax.grid(True, axis="x", color="lightgrey", zorder=0)
            hbars = ax.barh(  # 가로 막대 그래프 그리기
                range(len(data[i]["value"])),
                data[i]["value"],
                align="center",
                color=color_list,
                zorder=3
            )
            ax.set_yticks(range(len(data[i]["value"])))
            ax.set_yticklabels(data[i]["index"], fontsize=8)
            ax.invert_yaxis()
            if "lat" in data[i]["title"]:
                ax.xaxis.set_major_formatter(
                    ticker.FuncFormatter(FormatLatency))
            elif "iops" in data[i]["title"]:
                ax.xaxis.set_major_formatter(ticker.FuncFormatter(FormatIOPS))
            elif "bw" in data[i]["title"]:
                ax.xaxis.set_major_formatter(ticker.FuncFormatter(FormatKBW))
            else:
                ax.xaxis.set_major_formatter(ticker.EngFormatter())
            ax.tick_params(axis="x", labelrotation=30, labelsize=8)

            rects = ax.patches
            x_min, x_max = plt.gca().get_xlim()
            for rect in rects:  # 막대에 label 붙여서 값 표시
                x_val = rect.get_width()
                y_val = rect.get_y() + rect.get_height() / 2
                label = FormatSimpleFloat(x_val)
                x_offset = 5
                align = "left"
                # 막대의 크기가 subplot의 3/4보다 크면 label이 subplot을 넘어가는 것 방지
                if 0.75 < (x_val / x_max):
                    x_offset = -10
                    align = "right"
                plt.annotate(
                    label,
                    (x_val, y_val),
                    xytext=(x_offset, 0),
                    textcoords="offset points",
                    va="center",
                    ha=align,
                    fontsize=9
                )

        plt.tight_layout()
        plt.savefig(f"{pic_name}_result.png", dpi=200)
        plt.close(fig)
    except Exception as e:
        lib.printer.red(f"{__name__} [Error] {e}")
        plt.close(fig)


def DrawLogGraphWithType(data: dict, pic_name: str, type: str) -> None:
    """ Draw individual job graphs based on FIO log data on the PNG file.

    Args:
        data (dict): Raw data.
        pic_name (str): PNG file name.
        type (str): Should be "iops" or "bw" or "lat".
    """
    try:
        plt.clf()  # plot 초기화
        num_graph = len(data)
        # plot size setting(unit: inch)
        fig = plt.figure(figsize=(8, 3 * num_graph))

        for job in data:
            # subplot position(행, 렬, 순서)
            ax = plt.subplot(num_graph, 1, int(job))
            ax.set_title(job, fontsize=12)
            ax.grid(True, axis="y", color="lightgrey", zorder=0)
            if ("iops" == type):
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(FormatIOPS))
            elif ("bw" == type):
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(FormatKBW))
            elif ("lat" == type):
                ax.yaxis.set_major_formatter(
                    ticker.FuncFormatter(FormatLatency))
            else:
                ax.yaxis.set_major_formatter(ticker.EngFormatter())
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(FormatEpochTime))
            ax.tick_params(axis='y', labelrotation=30, labelsize=8)
            ax.tick_params(axis='x', labelrotation=0, labelsize=8)
            plt.scatter(data[job]["read"]["x"], data[job]
                        ["read"]["y"], s=10, label="read")  # 점 그래프
            plt.plot(data[job]["read"]["x"], data[job]["read"]["y"])  # 선 그래프
            plt.scatter(data[job]["write"]["x"], data[job]
                        ["write"]["y"], s=10, label="write")
            plt.plot(data[job]["write"]["x"], data[job]["write"]["y"])
            plt.legend(fontsize=8, loc="upper left", ncol=2)  # 범례 그리기

        plt.tight_layout()
        plt.savefig(pic_name, dpi=200)
        plt.close(fig)
    except Exception as e:
        lib.printer.red(f"{__name__} [Error] {e}")
        plt.close(fig)


def DrawLog(data: dict, pic_name: str) -> None:
    """ Draw some sets of graphs based on FIO log data on the PNG files.

    Args:
        data (dict): Raw data.
        pic_name (str): PNG file name prefix (pic_name_per_job_xxx.png)
    """
    DrawLogGraphWithType(data["iops"], f"{pic_name}_per_job_iops.png", "iops")
    DrawLogGraphWithType(data["bw"], f"{pic_name}_per_job_bw.png", "bw")
    DrawLogGraphWithType(data["clat"], f"{pic_name}_per_job_clat.png", "lat")
