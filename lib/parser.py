import argparse


class ArgParser:
    config = ""

    def __init__(self):
        parser = argparse.ArgumentParser(description="benchmark options")
        parser.add_argument(
            "--config",
            required=True,
            help="set specific json file"
        )
        args = parser.parse_args()
        ArgParser.config = args.config

    @classmethod
    def GetConfig(cls):
        return cls.config
