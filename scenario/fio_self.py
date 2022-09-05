import graph
import iogen
import lib
import node.node
import profile.profiler
import traceback


def play(tgts, inits, scenario, timestamp, data):
    try:  # Prepare sequence
        node_manager = node.node.NodeManager(tgts, inits)
        targets, initiators = node_manager.initialize()

        test_case_list = [
            {"name": "1_write", "rw": "write", "bs": "128k",
                "iodepth": "4", "time_based": "1", "runtime": "30"}
        ]

        grapher = graph.manager.Grapher(scenario, timestamp)
        prof = profile.profiler.Profiler(timestamp, targets, initiators)
    except Exception as e:
        lib.printer.red(traceback.format_exc())
        return data

    try:  # Test sequence
        for test_case in test_case_list:
            # setup fio_cmd
            fio_cmd_list = []
            for key in initiators:
                fio_cmd = iogen.fio.Fio(initiators[key], timestamp)
                fio_cmd.initialize()
                fio_cmd.update(test_case)
                fio_cmd_list.append(fio_cmd.stringify())

            # start profiler
            prof.start(test_case["name"], fio_cmd.get_interval())

            # run fio
            lib.printer.green(f" run -> {timestamp} {test_case['name']}")
            lib.subproc.sync_parallel_run(fio_cmd_list, True)

            # end profiler (copy output, draw graph)
            prof.end(f"{scenario['OUTPUT_DIR']}")

            # copy output
            for key in initiators:
                initiators[key].copy_output(
                    timestamp, test_case["name"], scenario["OUTPUT_DIR"])

            # draw graph
            for key in initiators:
                grapher.draw(initiators[key], test_case["name"])

    except Exception as e:
        lib.printer.red(traceback.format_exc())

    try:  # Wrapup sequence
        node_manager.finalize()
    except Exception as e:
        lib.printer.red(traceback.format_exc())

    return data
