from datetime import datetime
import importlib.util
import json
import lib
import os
import sys
import traceback


def play(config):
    print("\n --- [benchmark start] --- ")

    date_now = datetime.now()
    timestamp = date_now.strftime("%y%m%d_%H%M%S")

    # config verification
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

    # first access check
    for target in config["Targets"]:
        try:
            cmd = (
                f"sshpass -p {target['PW']} "
                f"ssh -o StrictHostKeyChecking=no "
                f"{target['ID']}@{target['NIC']['SSH']} "
                f"sudo nohup uname -a"
            )
            lib.printer.yellow(lib.subproc.sync_run(cmd))
        except Exception as e:
            lib.printer.yellow(traceback.format_exc())
    for initiator in config["Initiators"]:
        try:
            cmd = (
                f"sshpass -p {initiator['PW']} "
                f"ssh -o StrictHostKeyChecking=no "
                f"{initiator['ID']}@{initiator['NIC']['SSH']} "
                f"sudo nohup uname -a"
            )
            lib.printer.yellow(lib.subproc.sync_run(cmd))
        except Exception as e:
            lib.printer.yellow(traceback.format_exc())

    # ip update
    for target in config["Targets"]:
        for subsys in target["POS"]["SUBSYSTEMs"]:
            subsys["IP"] = target["NIC"][subsys["IP"]]
    for initiator in config["Initiators"]:
        for tgt in initiator["TARGETs"]:
            for target in config["Targets"]:
                if target["NAME"] == tgt["NAME"]:
                    tgt["IP"] = target["NIC"][tgt["IP"]]

    data = {}
    for scenario in config["Scenarios"]:
        try:
            if scenario.get("SUBPROC_LOG"):
                lib.subproc.set_print_log(scenario["SUBPROC_LOG"])
            else:
                lib.subproc.set_print_log(False)

            lib.subproc.sync_run(f"mkdir -p {scenario['OUTPUT_DIR']}")
            lib.subproc.sync_run(f"mkdir -p {scenario['OUTPUT_DIR']}/log")

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
