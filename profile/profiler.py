from typing import Dict
import node.initiator
import node.target
import profile.pcm


class Profiler:
    """ Profiler manages 3rd-party profiling tools
    """

    def __init__(self, timestamp: str, target_dict: Dict[str, node.target.Target],
                 initiator_dict: Dict[str, node.initiator.Initiator]) -> None:
        """ Initialize Profiler object.

        Args:
            timestamp (str): Will be included in output file name.
            target_dict (Dict[str, node.target.Target]): Target dict with name key.
            initiator_dict (Dict[str, node.initiator.Initiator]): Initiator dict with name key.
        """
        self.timestamp: str = timestamp
        self.target_dict: Dict[str, node.target.Target] = target_dict
        self.initiator_dict: Dict[str,
                                  node.initiator.Initiator] = initiator_dict

    def start(self, test_name: str, interval: int) -> None:
        """ Check profile config and turn on profling.

        Args:
            test_name (str): Will be included in output file name.
            interval (int): If possible, this value would be used for tool's option.
        """
        self.test_name = test_name
        self.interval = interval
        for target in self.target_dict.values():
            profile.pcm.start(target, self.test_name,
                              self.timestamp, self.interval)
        for initiator in self.initiator_dict.values():
            profile.pcm.start(initiator, self.test_name,
                              self.timestamp, self.interval)

    def end(self, output_dir: str) -> None:
        """ Stop profiling, Copy results and Draw graphs.

        Args:
            output_dir (str): Directory for profiled raw data.
        """
        for target in self.target_dict.values():
            profile.pcm.end(target, self.test_name, self.timestamp, output_dir)
        for initiator in self.initiator_dict.values():
            profile.pcm.end(initiator, self.test_name,
                            self.timestamp, output_dir)
