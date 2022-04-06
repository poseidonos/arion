import fio
import graph
import initiator
import json
import lib
import target
import traceback
from datetime import datetime


def play(json_targets, json_inits, json_scenario):
    lib.printer.green(f"\n -- '{__name__}' has began --")

    raw_date = datetime.now()
    now_date = raw_date.strftime("%y%m%d_%H%M%S")
    skip_workload = False

    # validate arguments, 인자로 받은 json 정보가 있는지 확인
    if 0 == len(json_targets):
        lib.printer.red(" TargetError: At least 1 target has to exist")
        return
    if 0 == len(json_inits):
        lib.printer.red(" InitiatorError: At least 1 initiator has to exist")
        return
    if 0 == len(json_scenario):
        lib.printer.red(" ScenarioError: At least 1 scenario has to exist")
        return

    # target prepare, validation check 및 bringup/setup 진행
    targets = {}
    for json_target in json_targets:
        try:
            target_obj = target.manager.Target(json_target)
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            return
        target_name = json_target["NAME"]

        try:
            target_obj.Prepare()
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            skip_workload = True
            target_obj.ForcedExit()
            break
        targets[target_name] = target_obj

    # init prepare, validation check 및 bringup/setup 진행
    initiators = {}
    for json_init in json_inits:
        try:
            init_obj = initiator.manager.Initiator(json_init)
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            skip_workload = True
            break
        init_name = json_init["NAME"]

        try:
            init_obj.Prepare()
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            skip_workload = True
            break
        initiators[init_name] = init_obj

    # run workload
    if not skip_workload:
        lib.printer.green(f" vdbench start")

        storage_definition = []

        workload_definitions = []

        run_definitions = []

        lib.printer.green(f" vdbench end")

    # init wrapup
    for key in initiators:
        try:
            initiators[key].Wrapup()
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            skip_workload = True

    # target warpup
    for key in targets:
        try:
            targets[key].Wrapup()
        except Exception as e:
            lib.printer.red(traceback.format_exc())
            targets[key].ForcedExit()
            skip_workload = True

    if skip_workload:
        lib.printer.red(f" -- '{__name__}' unexpected done --\n")
    else:
        lib.printer.green(f" -- '{__name__}' successfully done --\n")
