from abc import *
from typing import Tuple
import lib
import node
import traceback


class NodeManager:
    """ NodeManager delegates node rountine such as create, delete, bringup, wrapup, etc.
    """

    def __init__(self, target_list: list, initiator_list: list) -> None:
        """ Initialize NodeManager object with targets & initiators info.

        Args:
            target_list (list): Targets info from config.
            initiator_list (list): Initiators info from config.
        """
        self.target_list = target_list
        self.initiator_list = initiator_list
        self.targets = {}
        self.initiators = {}

    def initialize(self) -> Tuple[dict, dict]:
        """ Create Target objects and Initiator objects. Bring up each node.

        Returns:
            Tuple[dict, dict]: [Target dict with a target name as a key, Initiator dict with a initiator name as a key]
        """
        self.__create_targets()
        self.__create_initiators()
        return self.targets, self.initiators

    def finalize(self) -> None:
        """ Wrap up Target objects and Initiator objects.
        """
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

    def __create_targets(self) -> None:
        for target_dict in self.target_list:
            try:
                target_obj = node.target.Target(target_dict)
                target_obj.bring_up()
            except Exception as e:
                lib.printer.red(traceback.format_exc())
                target_obj.forced_exit()
                return
            target_name = target_dict["NAME"]
            self.targets[target_name] = target_obj

    def __create_initiators(self) -> None:
        for init_dict in self.initiator_list:
            try:
                init_obj = node.initiator.Initiator(init_dict)
                init_obj.bring_up()
            except Exception as e:
                lib.printer.red(traceback.format_exc())
                return
            init_name = init_dict["NAME"]
            self.initiators[init_name] = init_obj


class Node(metaclass=ABCMeta):
    @abstractmethod
    def bring_up(self):
        pass

    @abstractmethod
    def wrap_up(self):
        pass

    @abstractmethod
    def sync_run(self, cmd, ignore_err, sh):
        pass

    @abstractmethod
    def sync_parallel_run(self, cmd_list, ignore_err, sh):
        pass

    @abstractmethod
    def async_run(self, cmd, ignore_err, sh):
        pass

    @abstractmethod
    def async_parallel_run(self, cmd_list, ignore_err, sh):
        pass
