import argparse
import json
import lib
import os
import sys


def parse_config_file(file_path):
    print(f"open json cfg file: {file_path}")
    try:
        with open(file_path, "r") as f:
            config = json.load(f)
    except IOError:
        lib.printer.red(f"{__name__} [IOError] No such file or directory")
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        lib.printer.red(f"{__name__} [JSONDecodeError] {e}")
        sys.exit(1)
    return config


def update_list(define, config):
    for index, value in enumerate(define):
        if isinstance(value, dict):
            update_dict(value, config[index])
        elif isinstance(value, list):
            update_list(value, config[index])


def update_dict(define, config):
    for key, value in define.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict):
            update_dict(value, config[key])
        elif isinstance(value, list):
            update_list(value, config[key])
        else:
            config[key] = value


def define_to_config(define, config):
    update_dict(define, config)


class ArgParser:
    def __init__(self):
        parser = argparse.ArgumentParser(description="benchmark options")
        parser.add_argument(
            "-c", "--config",
            required=True,
            help="ARION specific json config file"
        )
        parser.add_argument(
            "-d", "--define",
            type=json.loads,
            default="{}",
            help="Definition of config option"
        )
        self.args = parser.parse_args()

    def get_config(self):
        return self.args.config

    def get_define(self):
        return self.args.define
