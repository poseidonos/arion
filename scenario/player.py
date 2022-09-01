from datetime import datetime
import enum
import importlib.util
import lib
import sys
import traceback


def play(config):
    print("\n --- [benchmark start] --- ")

    date_now = datetime.now()
    timestamp = date_now.strftime("%y%m%d_%H%M%S")

    # config verification
    if "TARGETs" not in config:
        lib.printer.red(
            f"{__name__} [KeyError] JSON file has no KEY 'TARGETs'")
        sys.exit(1)
    if "INITIATORs" not in config:
        lib.printer.red(
            f"{__name__} [KeyError] JSON file has no KEY 'INITIATORs'")
        sys.exit(1)
    if "SCENARIOs" not in config:
        lib.printer.red(
            f"{__name__} [KeyError] JSON file has no KEY 'SCENARIOs'")
        sys.exit(1)
    if 0 == len(config["TARGETs"]):
        lib.printer.red(" TargetError: At least 1 target has to exist")
        sys.exit(1)
    if 0 == len(config["INITIATORs"]):
        lib.printer.red(" InitiatorError: At least 1 initiator has to exist")
        sys.exit(1)
    if 0 == len(config["SCENARIOs"]):
        lib.printer.red(" ScenarioError: At least 1 scenario has to exist")
        sys.exit(1)

    # first access check
    for target in config["TARGETs"]:
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
    for initiator in config["INITIATORs"]:
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
    for target in config["TARGETs"]:
        for subsys in target["POS"]["SUBSYSTEMs"]:
            subsys["IP"] = target["NIC"][subsys["IP"]]
    for initiator in config["INITIATORs"]:
        for tgt in initiator["TARGETs"]:
            for target in config["TARGETs"]:
                if target["NAME"] == tgt["NAME"]:
                    tgt["IP"] = target["NIC"][tgt["IP"]]
    for scenario in config["SCENARIOs"]:
        if scenario.get("TARGETs"):
            for tgt_idx, sn_tgt in enumerate(scenario["TARGETs"]):
                if sn_tgt.get("POS") and sn_tgt["POS"].get("SUBSYSTEMs"):
                    for sn_tgt_subsys in sn_tgt["POS"]["SUBSYSTEMs"]:
                        if sn_tgt_subsys.get("IP"):
                            if sn_tgt.get("NIC") and sn_tgt["NIC"].get(sn_tgt_subsys["IP"]):
                                sn_tgt_subsys["IP"] = sn_tgt["NIC"][sn_tgt_subsys["IP"]]
                            else:
                                sn_tgt_subsys["IP"] = config["TARGETs"][tgt_idx]["NIC"][sn_tgt_subsys["IP"]]
        if scenario.get("INITIATORs"):
            for sn_init in scenario["INITIATORs"]:
                if sn_init.get("TARGETs"):
                    for sn_init_tgt in sn_init["TARGETs"]:
                        if sn_init_tgt.get("IP"):
                            for target in config["TARGETs"]:
                                if target["NAME"] == sn_init_tgt["NAME"]:
                                    sn_init_tgt["IP"] = target["NIC"][sn_init_tgt["IP"]]

    data = {}
    for scenario in config["SCENARIOs"]:
        try:
            if scenario.get("SUBPROC_LOG"):
                lib.subproc.set_print_log(scenario["SUBPROC_LOG"])
            else:
                lib.subproc.set_print_log(False)

            if scenario.get("TARGETs"):
                for idx, sn_tgt in enumerate(scenario["TARGETs"]):
                    if idx < len(config["TARGETs"]):
                        lib.parser.copy_dict(sn_tgt, config["TARGETs"][idx])
            if scenario.get("INITIATORs"):
                for idx, sn_init in enumerate(scenario["INITIATORs"]):
                    if idx < len(config["INITIATORs"]):
                        lib.parser.copy_dict(
                            sn_init, config["INITIATORs"][idx])

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
        data = module.play(config["TARGETs"], config["INITIATORs"],
                           scenario, timestamp, data)
        lib.printer.green(f"\n -- scenario: {scenario['NAME']} end --")

    print(" --- [benchmark done] --- \n")
    return 0
