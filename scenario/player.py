from datetime import datetime
import importlib
import json
import lib
import os
import sys


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
            module_name = "scenario." + scenario["NAME"]
        except KeyError:
            lib.printer.red(
                f"{__name__} [KeyError] JSON file Scenarios has no KEY 'NAME'")
            sys.exit(1)

        try:
            lib.subproc.sync_run(f"mkdir -p {scenario['OUTPUT_DIR']}")
            lib.subproc.sync_run(f"mkdir -p {scenario['OUTPUT_DIR']}/log")
        except KeyError:
            lib.printer.red(
                f"{__name__} [KeyError] JSON file Scenarios has no KEY 'OUTPUT_DIR'")
            sys.exit(1)
        except Exception as e:
            lib.printer.red(f"{__name__} [Error] {e}")
            sys.exit(1)

        if (scenario.get("SUBPROC_LOG") and scenario["SUBPROC_LOG"]):
            lib.subproc.set_print_log(True)

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            lib.printer.red(
                f"{__name__} [ImportError] '{module_name}' is not defined")
            sys.exit(1)

        if not hasattr(module, "play"):
            lib.printer.red(
                f"{__name__} [AttributeError] '{module_name}' has no attribute 'play'")
            sys.exit(1)
        lib.printer.green(f"\n -- scenario: {scenario['NAME']} start --")
        data = module.play(config["Targets"], config["Initiators"],
                           scenario, timestamp, data)
        lib.printer.green(f"\n -- scenario: {scenario['NAME']} end --")

    print(" --- [benchmark done] --- \n")
    return 0
