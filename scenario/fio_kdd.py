import graph
import iogen
import json
import lib
import node
import traceback


def play(json_targets, json_inits, json_scenario, timestamp, data):
    node_manager = node.NodeManager(json_targets, json_inits)
    targets, initiators = node_manager.initialize()

    graph_fio = graph.manager.Fio(
        json_scenario["OUTPUT_DIR"], timestamp, __name__)

    test_case_list = [
        {"name": "1_write", "rw": "write", "bs": "128k",
            "iodepth": "4", "time_based": "1", "runtime": "15"},
        {"name": "2_read", "rw": "read", "bs": "128k",
            "iodepth": "4", "time_based": "1", "runtime": "15"},
        {"name": "3_randwrite", "rw": "randwrite", "bs": "4k",
            "iodepth": "4", "time_based": "1", "runtime": "15"},
        {"name": "4_randread", "rw": "randread", "bs": "4k",
            "iodepth": "4", "time_based": "1", "runtime": "15"}
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
                fio_cmd.initialize(True)  # kdd setting True
                fio_cmd.update(test_case, [1, 3, 5])
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

    return data
