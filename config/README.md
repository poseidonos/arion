# Configuration

ARION provides a **specific JSON schemed** config file which consists of Targets, Initiators, and Scenarios.

## 1. Targets

User can set up multiple target nodes within Targets' value as a list.
```json
{
    "Targets": [
        {
            "NAME": "Target01",
            "ID": "user account",
            "PW": "user password",
            "NIC": {
                "SSH": "SSH IP addresss",
                "IP1": "Test IP1 address",
                "IP2": "Test IP2 address",
            },
            "PREREQUISITE": {
                "CPU": {
                    "RUN": true,
                    "SCALING": "max"
                }
            },
            "POS": {
                "DIR": "pos root directory",
                "BIN": "pos binary name",
                "CLI": "pos CLI name",
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
    ]
}
```

Each object in the list is constructed as shown in the table below.

| Key          | Value  | Option    | Description                                                  |
| ------------ | ------ | --------- | ------------------------------------------------------------ |
| NAME         | string | Mandatory | Target node name<br />User can take target object using this value from the code |
| ID           | string | Mandatory | Target node account (linux account)                          |
| PW           | string | Mandatory | Target node password (linux password)                        |
| NIC          | object | Mandatory | Network IP addresses to access and to test                   |
| PREREQUISITE | object | Optional  | Default value: `None`<br />Prerequisite setting before test  |
| POS          | object | Mandatory | POS setting                                                  |



### 1.1. NIC

| Key    | Value  | Option    | Description                                                  |
| ------ | ------ | --------- | ------------------------------------------------------------ |
| SSH    | string | Mandatory | IP address to use `sshpass`                                  |
| TestIP | string | Mandatory | IP address to test<br />This key name can be any value<br />`Targets>POS>SUBSYSTEMs>IP` uses this key name<br />`Initiators>Targets>IP` uses this key name |



### 1.2. PREREQUISITE

| Key      | Value  | Option   | Description      |
| -------- | ------ | -------- | ---------------- |
| CPU      | object | Optional | CPU setting      |
| SSD      | object | Optional | SSD setting      |
| MEMORY   | object | Optional | Memory setting   |
| NETWORK  | object | Optional | Network setting  |
| MODPROBE | object | Optional | Modprobe setting |
| SPDK     | object | Optional | SPDK setting     |
| DEBUG    | object | Optional | DEBUG setting    |

#### 1.2.1. CPU

| Key     | Value   | Option    | Description                                                  |
| ------- | ------- | --------- | ------------------------------------------------------------ |
| RUN     | boolean | Mandatory | If `true`, set all the CPU setting below                     |
| SCALING | string  | Optional  | CPU frequency & governor setting<br />Valid value: `min`, `max` |

#### 1.2.2. SSD

| Key       | Value   | Option    | Description                                        |
| --------- | ------- | --------- | -------------------------------------------------- |
| RUN       | boolean | Mandatory | If `true`, set all the SSD setting below           |
| FORMAT    | boolean | Optional  | If `true`, format all NVMe SSD except booting disk |
| UDEV_FILE | string  | Optional  | unvme custom(POS) setting, don't touch             |

#### 1.2.3. MEMORY

| Key           | Value   | Option    | Description                                                  |
| ------------- | ------- | --------- | ------------------------------------------------------------ |
| RUN           | boolean | Mandatory | If `true`, set all the MEMORY setting below                  |
| MAX_MAP_COUNT | int     | Optional  | Set vm.max_map_count                                         |
| DROP_CACHES   | int     | Optional  | Valid value: `1`, `2`, `3`<br />`1`: Clear PageCache only<br />`2`: Clear dentries & inodes<br />`3`: Clear all |

#### 1.2.4. NETWORK

| Key           | Value   | Option    | Description                                                  |
| ------------- | ------- | --------- | ------------------------------------------------------------ |
| RUN           | boolean | Mandatory | If `true`, set all the NETWORK setting below                 |
| IRQ_BALANCE   | string  | Optional  | Valid value: `start`, `stop`                                 |
| TCP_TUNE      | string  | Optional  | Valid value: `min`, `max`<br />core_mem, tcp_wmem, tcp_rmem, mtu_probing, window_scaling, slow_start setting |
| IRQ_AFFINITYs | list    | Optional  | IRQ affinity setting for each NIC<br />note: using ./test/script/set_irq_affinity_cpulist.sh |
| NICs          | list    | Optional  | Network interface setting                                    |

#### 1.2.5. MODPROBE

| Key  | Value   | Option    | Description                                   |
| ---- | ------- | --------- | --------------------------------------------- |
| RUN  | boolean | Mandatory | If `true`, set all the MODPROBE setting below |
| MODs | list    | Optional  | modules to load                               |

#### 1.2.6. SPDK

| Key             | Value   | Option    | Description                                                  |
| --------------- | ------- | --------- | ------------------------------------------------------------ |
| RUN             | boolean | Mandatory | If `true`, set all the SPDK setting below                    |
| HUGE_EVEN_ALLOC | string  | Optional  | Valid value:`yes`, `no`<br />SPDK hugepage alloc option<br />note: using ./lib/spdk/scripts/setup.sh |
| NRHUGE          | int     | Optional  | Number of hugepage<br />note: using ./lib/spdk/scripts/setup.sh |

#### 1.2.7. DEBUG

| Key          | Value   | Option    | Description                                |
| ------------ | ------- | --------- | ------------------------------------------ |
| RUN          | boolean | Mandatory | If `true`, set all the DEBUG setting below |
| ULIMIT       | string  | Optional  | Valid value: `soft`, `hard`, `unlimited`   |
| APPORT       | string  | Optional  | Valid value: `enable`, `disable`           |
| DUMP_DIR     | string  | Optional  | POS dump directory                         |
| CORE_PATTERN | string  | Optional  | POS core pattern                           |



### 1.3. POS

| Key           | Value   | Option    | Description                                                  |
| ------------- | ------- | --------- | ------------------------------------------------------------ |
| DIR           | string  | Mandatory | POS root directory                                           |
| BIN           | string  | Mandatory | POS binary name                                              |
| CLI           | string  | Mandatory | POS CLI name                                                 |
| CLI_LOCAL_RUN | boolean | Optional  | Default value: `false`<br />If true, bypass sshpass to compose POS<br />It executes more faster than using sshpass<br />Caution: ARION must be executed in the target node |
| CFG           | string  | Mandatory | POS config name                                              |
| LOG           | string  | Mandatory | POS log file name                                            |
| TELEMETRY     | boolean | Optional  | Default value: `true`                                        |
| LOGGER_LEVEL  | string  | Optional  | Default value: `info`<br />Valid value: `info`, `debug`, `warning`, `error`, `critical` |
| DIRTY_BRINGUP | boolean | Optional  | Default value: `false`                                       |
| TRANSPORT     | object  | Mandatory | Valid value: `tcp`, `rdma`                                   |
| SUBSYSTEMs    | list    | Mandatory | POS subsystems information                                   |
| DEVICEs       | list    | Mandatory | POS devices information                                      |
| ARRAYs        | list    | Mandatory | POS arrays information                                       |

#### 1.3.1. TRANSPORT

| Key               | Value  | Option    | Description                |
| ----------------- | ------ | --------- | -------------------------- |
| TYPE              | string | Mandatory | Valid value: `tcp`, `rdma` |
| NUM_SHARED_BUFFER | int    | Mandatory | Number of shared buffer    |

#### 1.3.2. SUBSYSTEMs

| Key            | Value  | Option    | Description                                                  |
| -------------- | ------ | --------- | ------------------------------------------------------------ |
| NUM_SUBSYSTEMS | int    | Mandatory | Number of subsystems to **create**<br />Each subsystem will follow NQN & SN rules below |
| NQN_PREFIX     | string | Mandatory | Prefix of NQN                                                |
| NQN_INDEX      | int    | Mandatory | Start index of NQN<br />This value will be suffix of NQN with :03d format<br />This value increases one by one until it reaches the NUM_SUBSYSTEMS |
| SN_PREFIX      | string | Mandatory | Prefix of serial number                                      |
| SN_INDEX       | int    | Mandatory | Start index of serial number<br />This value will be suffix of SN with :03d format<br />This value increases one by one until it reaches the NUM_SUBSYSTEMS |
| IP             | string | Mandatory | IP address to add listener for these subsystems              |
| PORT           | int    | Mandatory | PORT  number to add listener for these subsystems            |

#### 1.3.3. DEVICEs

| Key        | Value  | Option    | Description      |
| ---------- | ------ | --------- | ---------------- |
| NAME       | string | Mandatory | Device name      |
| TYPE       | string | Mandatory | Device type      |
| NUM_BLOCKS | int    | Mandatory | Number of blocks |
| BLOCK_SIZE | int    | Mandatory | Block size       |
| NUMA       | int    | Mandatory | Numa node        |

#### 1.3.4. ARRAYs

| Key               | Value   | Option    | Description                                                  |
| ----------------- | ------- | --------- | ------------------------------------------------------------ |
| NAME              | string  | Mandatory | Array name                                                   |
| RAID_OR_MEDIA     | string  | Mandatory | Array Raid or Media type<br />Valid value: `RAID5`, `RAID0`, `ZNS`, `TLC`, `NVRAM`, ... |
| WRITE_THROUGH     | boolean | Optional  | Default value: `false`<br />Host write mode                  |
| USER_DEVICE_LIST  | string  | Mandatory | user nvme devices                                            |
| SPARE_DEVICE_LIST | string  | Mandatory | spare nvme devices                                           |
| BUFFER_DEV        | string  | Mandatory | buffer device name                                           |
| VOLUMEs           | list    | Mandatory | volume information                                           |

###### 1.3.4.1. VOLUMEs

| Key            | Value  | Option    | Description                                                  |
| -------------- | ------ | --------- | ------------------------------------------------------------ |
| NUM_VOLUMES    | int    | Mandatory | Number of volumes to **create & mount**<br />Each volume will follow NAME rules below |
| NAME_PREFIX    | string | Mandatory | Prefix of name                                               |
| NAME_INDEX     | int    | Mandatory | Start index of name<br />This value will be suffix of name with :03d format<br />This value increases one by one until it reaches the NUM_VOLUMES |
| SIZE_MiB       | int    | Mandatory | Volume size                                                  |
| USE_SUBSYSTEMS | int    | Mandatory | Number of subsystems to mount these volumes                  |
| NQN_PREFIX     | string | Mandatory | Prefix of NQN to mount                                       |
| NQN_INDEX      | int    | Mandatory | Start index of NQN to mount<br />This value will be suffix of name with :03d format<br />This value increases one by one until it reaches the USE_SUBSYSTEMS<br />If NUM_VOLUMES > USE_SUBSYSTEMS, NQN_INDEX follows round-robin policy |



## 2. Initiators

User can set up multiple initiator nodes within Initiators' value as a list.
```json
{
    "Initiators": [
        {
            "NAME": "Initiator01",
            "ID": "user account",
            "PW": "user password",
            "NIC": {
                "SSH": "SSH IP addresss"
            },
            "PREREQUISITE": {
                "CPU": {
                    "RUN": true,
                    "SCALING": "max"
                },
                "MEMORY": {
                    "RUN": true,
                    "MAX_MAP_COUNT": 65535,
                    "DROP_CACHES": 3
                }
            },
            "SPDK": {
                "DIR": "spdk root directory",
                "TRANSPORT": "tcp"
            },
            "TARGETs": [
                {
                    "NAME": "Target01",
                    "TRANSPORT": "tcp",
                    "IP": "IP1",
                    "PORT": 1158,
                    "KDD_MODE": true,
                    "SUBSYSTEMs": [
                        {
                            "NUM_SUBSYSTEMS": 3,
                            "NQN_PREFIX": "nqn.2022-04.pos\\:subsystem",
                            "NQN_INDEX": 1,
                            "SN_PREFIX": "POS00000000000",
                            "SN_INDEX": 1,
                            "NUM_NS": 1,
                            "NS_INDEX": 1
                        }
                    ]
                }
            ]
        }
    ]
}
```

Each object in the list is constructed as shown in the table below.

| Key          | Value  | Option    | Description                                     |
| ------------ | ------ | --------- | ----------------------------------------------- |
| NAME         | string | Mandatory | Initiator node name                             |
| ID           | string | Mandatory | Initiator node account                          |
| PW           | string | Mandatory | Initiator node password                         |
| NIC          | object | Mandatory | Network card IP                                 |
| PREREQUISITE | object | Optional  | Default value: `None`<br />Prerequisite setting |
| SPDK         | object | Mandatory | SPDK setting (if use user-space NVMe-oF)        |
| TARGETs      | list   | Mandatory | Back-end storage which connect with NVMe-oF     |



### 2.1. NIC

| Key  | Value  | Option    | Description                 |
| ---- | ------ | --------- | --------------------------- |
| SSH  | string | Mandatory | IP address to use `sshpass` |



### 2.2. PREREQUISITE

Same as `Targets>PREREQUISITE` option



### 2.3. SPDK

| Key       | Value  | Option    | Description                |
| --------- | ------ | --------- | -------------------------- |
| DIR       | string | Mandatory | SPDK root directory        |
| TRANSPORT | string | Mandatory | Valid value: `tcp`, `rdma` |



### 2.4. TARGETs

An initiator object can have multiple targets which consist of POS storage will be connected via NVMe-oF.

| Key        | Value   | Option    | Description                                                  |
| ---------- | ------- | --------- | ------------------------------------------------------------ |
| NAME       | string  | Mandatory | Target node name to connect                                  |
| TRANSPORT  | string  | Mandatory | Valid value: `tcp`, `rdma`                                   |
| IP         | string  | Mandatory | Target node's `NIC>Key` name to connect                      |
| PORT       | int     | Mandatory | Port to connect                                              |
| KDD_MODE   | boolean | Optional  | Default value: `false`<br />Connection option (Kernel Device Driver) |
| SUBSYSTEMs | list    | Mandatory | Target node's subsystem to connect                           |

#### 2.4.1. SUBSYSTEMs

Through bring-up sequence, those subsystems will be automatically connected.

| Key            | Value  | Option    | Description                                                  |
| -------------- | ------ | --------- | ------------------------------------------------------------ |
| NUM_SUBSYSTEMS | int    | Mandatory | Number of subsystems to **connect**<br />Each subsystem will follow NQN rules below |
| NQN_PREFIX     | string | Mandatory | Prefix of NQN                                                |
| NQN_INDEX      | int    | Mandatory | Start index of NQN<br />This value will be suffix of NQN with :03d format |
| SN_PREFIX      | string | Optional  | Prefix of serial number<br />This value will be used at KDD_MODE |
| SN_INDEX       | int    | Optional  | Start index of serial number<br />This value will be suffix of SN with :03d format<br />This value will be used at KDD_MODE |
| NUM_NS         | int    | Mandatory | Number of namespace to connect each subsystem                |
| NS_INDEX       | int    | Mandatory | Start index of namespace                                     |



## 3. Scenarios

User can set up multiple test scenarios within Scenarios' value as a list.
```json
{
    "Scenarios": [
        {
            "PATH": "./relative_scenario_path/scenario_01.py",
            "NAME": "scenario_01",
            "OUTPUT_DIR": "./output_01",
            "RESULT_FORMAT": "junit_xml",
            "SUBPROC_LOG": true
        },
        {
            "PATH": "/absolute_scenario_path/scenario_02.py",
            "NAME": "scenario_02",
            "OUTPUT_DIR": "./output_02"
        }
    ]
}
```

Each object in the list is constructed as shown in the table below.

| Key           | Value   | Option    | Description                                                  |
| ------------- | ------- | --------- | ------------------------------------------------------------ |
| PATH          | string  | Mandatory | Test scenario file path                                      |
| NAME          | string  | Mandatory | Test scenario file name                                      |
| OUTPUT_DIR    | string  | Mandatory | Directory where all output will be stored                    |
| RESULT_FORMAT | string  | Optional  | Default value: `junit_xml`<br />Valid value: `junit_xml`     |
| SUBPROC_LOG   | boolean | Optional  | Default value: `false`<br />If `true`, print subprocess message |