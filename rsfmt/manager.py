from typing import List
import rsfmt.junit_xml


class Formatter:
    """ Formatter is a abstract class to handle benchmark result and status.
    """

    def __init__(self, scenario: dict, timestamp: str) -> None:
        """ Initialize Formatter object with scenario data.

        Args:
            scenario (dict): Parse result format.
            timestamp (str): Will be included within file prefix.
        """
        if scenario.get("RESULT_FORMAT"):
            if scenario["RESULT_FORMAT"] == "junit_xml":
                self.fmt = rsfmt.junit_xml.JunitXml(scenario, timestamp)
            else:
                self.fmt = rsfmt.junit_xml.JunitXml(scenario, timestamp)
        else:
            self.fmt = rsfmt.junit_xml.JunitXml(scenario, timestamp)

    def add_test_case(self, name: str, status: str = "error") -> None:
        """ Add test case.

        Args:
            name (str): Test case name.
            status (str, optional): One of (error | skipped | pass | fail). Defaults to "error".
        """
        self.fmt.add_test_case(name, status)

    def add_test_cases(self, names: List[str], status: str = "error") -> None:
        """ Add test cases.

        Args:
            names (List[str]): List of test case name.
            status (str, optional): One of (error | skipped | pass | fail). Defaults to "error".
        """
        self.fmt.add_test_cases(names, status)

    def start_test(self, name: str) -> None:
        """ Start a test with current timestamp. Do add_test_case(s) first.

        Args:
            name (str): This name has to be one of test cases' name.
        """
        self.fmt.start_test(name)

    def end_test(self, name: str, status: str, message: str = "") -> None:
        """ End a test with status and message.

        Args:
            name (str): This name has to be one of test cases' name.
            status (str): error | skipped | pass | fail
            message (str, optional): If status is not pass, this message will be saved. Defaults to "".
        """
        self.fmt.end_test(name, status, message)

    def write_file(self) -> None:
        """ Write result data as a file with specific format
        """
        self.fmt.write_file()
