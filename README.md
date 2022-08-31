# ARION

ARION is a test framework that supports to use 3rd-party benchmark tools in the same manner. ARION abstracts and maintains many interfaces(kernel, poseidonos-cli, nvme-cli, ...) so that user can focus on test scenario itself.



## 1. Install requirements

If it's first time to use ARION, you need to check your python version is higher than 3.6.

### Update pip
```bash
pip3 install pip --upgrade # pip version should be higher than 21.3.1
```

### Install requirements
```bash
pip3 install -r requirements.txt
```



## 2. Configuration

In ARION configuration, user can compose multi-POS topology(array, volume, subsystem, ...), multi-host(initiator) back-end storage, test scenarios. For more details: [ARION config guide](config/README.md)

```json
{
    "Targets": [
        {
            "NAME": "target name",
            "ID": "account",
            "PW": "password",
            "NIC": {
                "SSH": "ip address for sshpass",
                "IP1": "ip address for testing"
            },
            "POS": {
                "DIR": "pos root directory",
                "BIN": "poseidonos",
                "CLI": "poseidonos-cli",
                "CFG": "pos.conf",
                "LOG": "pos.log",
                "TELEMETRY": false,
                "LOGGER_LEVEL": "info",
                "TRANSPORT": {
                    "TYPE": "tcp",
                    "NUM_SHARED_BUFFER": 4096
                },
                "SUBSYSTEMs": [
                    {
                        "NUM_SUBSYSTEMS": 3,
                        "NQN_PREFIX": "nqn.2022-04.pos:subsystem",
                        "NQN_INDEX": 1,
                        "SN_PREFIX": "POS00000000000",
                        "SN_INDEX": 1,
                        "IP": "IP1",
                        "PORT": 1158
                    }
                ],
                "DEVICEs": [
                    {
                        "NAME": "uram0",
                        "TYPE": "uram",
                        "NUM_BLOCKS": 2097152,
                        "BLOCK_SIZE": 512,
                        "NUMA": 0
                    }
                ],
                "ARRAYs": [
                    {
                        "NAME": "ARR0",
                        "RAID_OR_MEDIA": "RAID5",
                        "WRITE_THROUGH": false,
                        "USER_DEVICE_LIST": "unvme-ns-0,unvme-ns-1,unvme-ns-2",
                        "SPARE_DEVICE_LIST": "unvme-ns-3",
                        "BUFFER_DEV": "uram0",
                        "VOLUMEs": [
                            {
                                "NUM_VOLUMES": 3,
                                "NAME_PREFIX": "VOL",
                                "NAME_INDEX": 1,
                                "SIZE_MiB": 2048,
                                "USE_SUBSYSTEMS": 3,
                                "NQN_PREFIX": "nqn.2022-04.pos:subsystem",
                                "NQN_INDEX": 1
                            }
                        ]
                    }
                ]
            }
        }
    ],
    "Initiators": [
        {
            "NAME": "initiator name",
            "ID": "account",
            "PW": "password",
            "NIC": {
                "SSH": "ip address for sshpass"
            },
            "SPDK": {
                "DIR": "spdk root directory",
                "TRANSPORT": "tcp"
            },
            "TARGETs": [
                {
                    "NAME": "target name",
                    "TRANSPORT": "tcp",
                    "IP": "target's IP key(in NIC object) for testing",
                    "PORT": 1158,
                    "SUBSYSTEMs": [
                        {
                            "NUM_SUBSYSTEMS": 3,
                            "NQN_PREFIX": "nqn.2022-04.pos\\:subsystem",
                            "NQN_INDEX": 1,
                            "NUM_NS": 1,
                            "NS_INDEX": 1
                        }
                    ]
                }
            ]
        }
    ],
    "Scenarios": [
        {
            "PATH": "scenario_path/scenario_name.py",
            "NAME": "scenario_name",
            "OUTPUT_DIR": "./output",
            "RESULT_FORMAT": "junit_xml",
            "SUBPROC_LOG": true
        }
    ]
}
```



## 3. Run ARION

```bash
python3 tool/arion/benchmark.py [-h] -c CONFIG [-d DEFINE]
```



## 4. Unit Test

```bash
python3 -m unittest -v # run all tc
python3 -m unittest test/specific_file.py -v # run specific tc
```
