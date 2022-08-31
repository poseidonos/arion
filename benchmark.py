import scenario
import lib

arg_data = lib.parser.ArgParser()

config_file = arg_data.get_config()
config = lib.parser.parse_config_file(config_file)

define = arg_data.get_define()
lib.parser.copy_dict(define, config)

scenario.player.play(config)
