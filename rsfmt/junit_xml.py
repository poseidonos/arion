import datetime


class JunitXml:
    def __init__(self, scenario, timestamp):
        self.title = scenario["NAME"]
        self.dir = scenario["OUTPUT_DIR"]
        self.timestamp = timestamp
        self.ts_start = datetime.datetime.now()
        self.ts_curr = datetime.datetime.now()
        self.tc_list = []
        self.valid_status = ['error', 'skipped', 'pass', 'fail']

    def add_test_case(self, name, status):
        if status not in self.valid_status:
            raise Exception((
                f"JunitXml status value has to be one of these:"
                f" {self.valid_status}"
            ))
        test_case = {}
        test_case["name"] = name
        test_case["status"] = status
        test_case["message"] = "Not Executed"
        test_case["classname"] = self.title
        test_case["time"] = 0
        test_case["timestamp"] = self.ts_start.replace(
            microsecond=0).isoformat()
        self.tc_list.append(test_case)

    def add_test_cases(self, name_list, status):
        for name in name_list:
            self.add_test_case(name, status)

    def start_test(self, name):
        self.ts_curr = datetime.datetime.now()
        for test_case in self.tc_list:
            if name == test_case["name"]:
                test_case["timestamp"] = self.ts_curr.replace(
                    microsecond=0).isoformat()

    def end_test(self, name, status, message):
        if status not in self.valid_status:
            raise Exception((
                f"JunitXml status value has to be one of these:"
                f" {self.valid_status}"
            ))
        tc_end = datetime.datetime.now()
        test_time = (tc_end - self.ts_curr).total_seconds()
        for test_case in self.tc_list:
            if name == test_case["name"]:
                test_case["time"] = test_time
                test_case["status"] = status
                test_case["message"] = message

    def write_file(self):
        ts_end = datetime.datetime.now()
        total_time = (ts_end - self.ts_start).total_seconds()
        failures = 0
        errors = 0
        skipped = 0
        for test_case in self.tc_list:
            if test_case["status"] == "error":
                errors += 1
            elif test_case["status"] == "fail":
                failures += 1
            elif test_case["status"] == "skipped":
                skipped += 1

        f = open(f"{self.dir}/{self.timestamp}_{self.title}.xml", "w")
        # header
        f.write(f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        # testsuites
        f.write((
            f"<testsuites name=\"{self.title}\" tests=\"{len(self.tc_list)}\" "
            f"failures=\"{failures}\" errors=\"{errors}\" skipped=\"{skipped}\" "
            f"disabled=\"0\" time=\"{total_time}\" "
            f"timestamp=\"{self.ts_start.replace(microsecond=0).isoformat()}\">\n"
        ))
        # testsuite
        f.write((
            f"  <testsuite name=\"{self.title}\" tests=\"{len(self.tc_list)}\" "
            f"failures=\"{failures}\" errors=\"{errors}\" skipped=\"{skipped}\" "
            f"disabled=\"0\" time=\"{total_time}\" "
            f"timestamp=\"{self.ts_start.replace(microsecond=0).isoformat()}\">\n"
        ))
        # testcase
        for test_case in self.tc_list:
            f.write((
                f"    <testcase name=\"{test_case['name']}\" "
                f"status=\"{test_case['status']}\" "
                f"time=\"{test_case['time']}\" "
                f"timestamp=\"{test_case['timestamp']}\" "
                f"classname=\"{test_case['classname']}\""
            ))
            if test_case["status"] == "error":
                f.write((
                    f">\n"
                    f"      <error message=\"unexpected error\" type=\"\">\n"
                    f"        {test_case['message']}</error>\n"
                    f"    </testcase>\n"
                ))
            elif test_case["status"] == "fail":
                f.write((
                    f">\n"
                    f"      <failure message=\"test failed\" type=\"\">\n"
                    f"        {test_case['message']}</failure>\n"
                    f"    </testcase>\n"
                ))
            elif test_case["status"] == "skipped":
                f.write((
                    f">\n"
                    f"      <skipped />\n"
                    f"    </testcase>\n"
                ))
            else:
                f.write(" />\n")

        f.write(f"  </testsuite>\n")
        f.write(f"</testsuites>\n")
        f.close()

        f = open(f"{self.dir}/{self.timestamp}_{self.title}.xml", "r")
        file_data = f.read()
        print(file_data)
        f.close()
