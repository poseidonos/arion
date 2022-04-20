from datetime import datetime
import importlib.util
import json
import lib
import os
import sys
import traceback


def play(json_cfg_file):
    print("\n --- [benchmark start] --- ")
    print("open json cfg file: " + json_cfg_file)

    date_now = datetime.now()
    timestamp = date_now.strftime("%y%m%d_%H%M%S")

    try:
        with open(json_cfg_file, "r") as f:
            config = json.load(f)
    except IOError:
        lib.printer.red(f"{__name__} [IOError] No such file or directory")
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        lib.printer.red(f"{__name__} [JSONDecodeError] {e}")
        sys.exit(1)

    if "Targets" not in config:
        lib.printer.red(
            f"{__name__} [KeyError] JSON file has no KEY 'Targets'")
        sys.exit(1)
    if "Initiators" not in config:
        lib.printer.red(
            f"{__name__} [KeyError] JSON file has no KEY 'Initiators'")
        sys.exit(1)
    if "Scenarios" not in config:
        lib.printer.red(
            f"{__name__} [KeyError] JSON file has no KEY 'Scenarios'")
        sys.exit(1)
    if 0 == len(config["Targets"]):
        lib.printer.red(" TargetError: At least 1 target has to exist")
        sys.exit(1)
    if 0 == len(config["Initiators"]):
        lib.printer.red(" InitiatorError: At least 1 initiator has to exist")
        sys.exit(1)
    if 0 == len(config["Scenarios"]):
        lib.printer.red(" ScenarioError: At least 1 scenario has to exist")
        sys.exit(1)

    data = {}
    for scenario in config["Scenarios"]:
        try:
            lib.subproc.sync_run(f"mkdir -p {scenario['OUTPUT_DIR']}")
            lib.subproc.sync_run(f"mkdir -p {scenario['OUTPUT_DIR']}/log")

            if (scenario.get("SUBPROC_LOG") and scenario["SUBPROC_LOG"]):
                lib.subproc.set_print_log(True)

            spec = importlib.util.spec_from_file_location(
                scenario["NAME"], scenario["PATH"])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            break

        if not hasattr(module, "play"):
            lib.printer.red(
                f"{__name__} {scenario['NAME']} has no 'play' function")
            break

        lib.printer.green(f"\n -- scenario: {scenario['NAME']} start --")
        data = module.play(config["Targets"], config["Initiators"],
                           scenario, timestamp, data)
        lib.printer.green(f"\n -- scenario: {scenario['NAME']} end --")

    print(" --- [benchmark done] --- \n")
    return 0
