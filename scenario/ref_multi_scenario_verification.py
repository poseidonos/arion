import graph
import iogen
import json
import lib
import node
import traceback


def play(json_targets, json_inits, json_scenario, timestamp, data):
    initiators = data["Initiators"]
    graph_fio = data["GraphFio"]

    bs_list = ["512", "4k", "128k", "512-128k"]
    rw_list = ["write", "randwrite", "randrw"]
    test_case_list = []
    test_case_num = 1
    for bs in bs_list:
        for rw in rw_list:
            test_case = {}
            test_case["name"] = f"{test_case_num:02d}_{bs}_{rw}"
            test_case["bs"] = bs
            test_case["rw"] = rw
            test_case["io_size"] = "100m"
            test_case["verify"] = "md5"
            test_case_num += 1
            test_case_list.append(test_case)

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
            lib.subproc.sync_parallel_run(fio_cmd_set, True)
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

    return data
