from pathlib import Path
import argparse
import json
from tokenize import String
import lib
import os
import sys


def parse_str_to_dict(str_data: str, ignore_err: bool = False) -> dict:
    """ Parse string data to dict data and return dict data.
    If it's invalid, raise Exception with the raw file data.

    Args:
        str_data (str): string data to parse
        ignore_err (bool, optional): Ignore error. Defaults to False.

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        dict: load JSON to dict
    """
    index = str_data.find('{')
    if index == -1:
        raise Exception(f"Unexpected error: {str_data}")
    else:
        if index != 0:
            if ignore_err:
                lib.printer.red(f"Error(but ignored by option)!!!\n{str_data[:index]}")
            else:
                raise Exception(f"Unexpected error: {str_data[:index]}")
        return json.loads(str_data[index:])


def parse_json_file(file_path: str) -> dict:
    """ Read a file(should be JSON format) and return dict data.
    If it's invalid, raise Exception with the raw file data.

    Args:
        file_path (str): file path and name

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        dict: load JSON to dict
    """
    str_data = Path(file_path).read_text()
    index = str_data.find('{')
    if index == -1:
        raise Exception(f"Unexpected error: {str_data}")
    else:
        if index != 0:
            raise Exception(f"Unexpected error: {str_data[:index]}")
        return json.loads(str_data[index:])


def parse_config_file(file_path: str) -> dict:
    """ Read config file(should be JSON format) and return dict data.

    Args:
        file_path (str): file path and name

    Returns:
        dict: load JSON to dict
    """
    print(f"open json cfg file: {file_path}")
    try:
        with open(file_path, "r") as f:
            config = json.load(f)
    except IOError:
        lib.printer.red(f"{__name__} [IOError] No such file or directory")
        f.close()
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        lib.printer.red(f"{__name__} [JSONDecodeError] {e}")
        f.close()
        sys.exit(1)
    f.close()
    return config


def copy_list(src: list, dst: dict) -> None:
    """ Copy from src list to dst dict.

    Args:
        src (list): source data
        dst (dict): destination data
    """
    for index, value in enumerate(src):
        if isinstance(value, dict):
            copy_dict(value, dst[index])
        elif isinstance(value, list):
            copy_list(value, dst[index])


def copy_dict(src: dict, dst: dict) -> None:
    """ Copy from src dict to dst dict.

    Args:
        src (dict): source data
        dst (dict): destination data
    """
    for key, value in src.items():
        if key not in dst:
            dst[key] = value
        elif isinstance(value, dict):
            copy_dict(value, dst[key])
        elif isinstance(value, list):
            copy_list(value, dst[key])
        else:
            dst[key] = value


class ArgParser:
    """ Using argparse library, Provide Arg options
    """

    def __init__(self):
        parser = argparse.ArgumentParser(description="benchmark options")
        parser.add_argument(
            "-c", "--config",
            type=str,
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

    def get_config(self) -> str:
        return self.args.config

    def get_define(self) -> dict:
        return self.args.define
