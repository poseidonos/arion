import graph
import iogen
import json
import lib
import node
import traceback


def play(json_targets, json_inits, json_scenario, timestamp):
    node_manager = node.NodeManager(json_targets, json_inits)
    targets, initiators = node_manager.initialize()

    graph_fio = graph.manager.Fio(
        json_scenario["OUTPUT_DIR"], timestamp, __name__)

    test_case_list = [
        {"name": "1_sw", "rw": "write", "bs": "128k", "iodepth": "4", "io_size": "100%",
            "time_based": "0", "runtime": "0", "log_avg_msec": "30000"},
        {"name": "2_sr", "rw": "read", "bs": "128k", "iodepth": "4", "io_size": "1t",
            "time_based": "1", "runtime": "60", "log_avg_msec": "2000"},
        {"name": "3_rw", "rw": "randwrite", "bs": "4k", "iodepth": "128",
            "io_size": "4t", "time_based": "1", "runtime": "60", "log_avg_msec": "2000"},
        {"name": "4_sus", "rw": "randwrite", "bs": "4k", "iodepth": "128", "io_size": "4t",
            "time_based": "1", "runtime": "28800", "log_avg_msec": "576000"},
        {"name": "5_rw", "rw": "randwrite", "bs": "4k", "iodepth": "128",
            "io_size": "4t", "time_based": "1", "runtime": "600", "log_avg_msec": "20000"},
        {"name": "6_rr", "rw": "randread", "bs": "4k", "iodepth": "128",
            "io_size": "4t", "time_based": "1", "runtime": "600", "log_avg_msec": "20000"},
        {"name": "7_mix", "rw": "randrw", "rwmixread": "70", "bs": "16k", "iodepth": "32",
            "io_size": "4t", "time_based": "1", "runtime": "600", "log_avg_msec": "20000"}
    ]

    test_stop = False
    for test_case in test_case_list:
        if (test_stop):
            break

        # setup fio_cmd
        fio_cmd_set = []
        for key in initiators:
            try:
                fio_cmd = iogen.fio.Fio(initiators[key], timestamp)
                fio_cmd.initialize()
                fio_cmd.update(test_case)
                fio_cmd_set.append(fio_cmd.stringify())
            except Exception as e:
                lib.printer.red(traceback.format_exc())
                test_stop = True
                break

        # run fio
        try:
            lib.printer.green(f" run -> {timestamp} {test_case['name']}")
            lib.subproc.parallel_run(fio_cmd_set)
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            break

        # draw graph
        for key in initiators:
            try:
                graph_fio.copy_data(initiators[key], test_case["name"])
                graph_fio.draw_graph(initiators[key], test_case["name"])
            except Exception as e:
                lib.printer.red(traceback.format_exc())
                test_stop = True
                break

    node_manager.finalize()
