from comets.parser.my_parser import create_parser, check_config, update_config
from comets.config.print import print_config


def run():
    # Configuration
    parser = create_parser()
    args = parser.parse_args()
    update_config(args)
    check_config()
    print_config()
