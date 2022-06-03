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

    def add_test_case(self, name, status="error"):
        self.fmt.add_test_case(name, status)

    def add_test_cases(self, name_list, status="error"):
        self.fmt.add_test_cases(name_list, status)

    def start_test(self, name):
        self.fmt.start_test(name)

    def end_test(self, name, status, message=""):
        self.fmt.end_test(name, status, message)

    def write_file(self):
        self.fmt.write_file()
