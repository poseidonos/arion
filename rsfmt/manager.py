import rsfmt.junit_xml


class Formatter:
    def __init__(self, scenario, timestamp):
        if scenario.get("RESULT_FORMAT"):
            if scenario["RESULT_FORMAT"] == "junit_xml":
                self.fmt = rsfmt.junit_xml.JunitXml(scenario, timestamp)
            else:
                self.fmt = rsfmt.junit_xml.JunitXml(scenario, timestamp)
        else:
            self.fmt = rsfmt.junit_xml.JunitXml(scenario, timestamp)

    def add_test_cases(self, tc_list):
        self.fmt.add_test_cases(tc_list)

    def start_test(self, tc_name):
        self.fmt.start_test(tc_name)

    def end_test(self, tc_name, status, message=""):
        if status == "pass" or status == "fail":
            self.fmt.end_test(tc_name, status, message)
        else:
            raise Exception("status value has to be 'pass' or 'fail'")

    def write_file(self):
        self.fmt.write_file()
