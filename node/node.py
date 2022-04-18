#from node.initiator import *
import json
import lib
import node
import traceback


class NodeManager:
    def __init__(self, json_targets, json_initiators):
        self.json_targets = json_targets
        self.json_initiators = json_initiators
        self.targets = {}
        self.initiators = {}

    def initialize(self):
        self.create_targets()
        self.create_initiators()
        return self.targets, self.initiators

    def finalize(self) -> None:
        for key in self.initiators:
            try:
                self.initiators[key].wrap_up()
            except Exception as e:
                lib.printer.red(traceback.format_exc())

        for key in self.targets:
            try:
                self.targets[key].wrap_up()
            except Exception as e:
                lib.printer.red(traceback.format_exc())

    def create_targets(self) -> None:
        for json_target in self.json_targets:
            try:
                target_obj = node.target.Target(json_target)
                target_obj.bring_up()
            except Exception as e:
                lib.printer.red(traceback.format_exc())
                target_obj.forced_exit()
                return
            target_name = json_target["NAME"]
            self.targets[target_name] = target_obj

    def create_initiators(self) -> None:
        for json_init in self.json_initiators:
            try:
                init_obj = node.initiator.Initiator(json_init)
                init_obj.bring_up()
            except Exception as e:
                lib.printer.red(traceback.format_exc())
                return
            init_name = json_init["NAME"]
            self.initiators[init_name] = init_obj
