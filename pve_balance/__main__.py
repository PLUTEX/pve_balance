import logging
import logging.config

from . import balance


def main():
    from configparser import ConfigParser
    import argparse
    import sys
    import os

    def loglevel_to_int(level):
        try:
            return int(level)
        except ValueError:
            try:
                return getattr(logging, level.upper())
            except AttributeError:
                raise argparse.ArgumentTypeError(
                    "{} is not a valid loglevel".format(level)
                )

    configpaths = [
        os.path.join(base, 'pve-balance.ini')
        for base in (
            '.',
            os.getenv('APPDATA', os.getenv('XDG_CONFIG_HOME', os.path.join(os.getenv('HOME'), '.config'))),
            '/etc',
        )
    ]

    config = ConfigParser()
    if not config.read(configpaths):
        print("Could not read config from any of the following locations:", file=sys.stderr)
        for configpath in configpaths:
            print(configpath, file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Balance VMs in a Proxmox Virtual Environment cluster."
    )
    parser.add_argument("host")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="""
            Exclude these cluster nodes from the target calculations.
            This will migrate all VMs from these nodes onto others and not
            migrate any VMs onto these nodes.
        """
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        help="Just calculate the migrations, but don't execute them"
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for all migrations to finish before exiting",
    )
    parser.add_argument("--loglevel", metavar="LEVEL")
    args = parser.parse_args()

    config["pve"]["host"] = args.host

    if args.loglevel:
        config["handler_console"]["level"] = args.loglevel.upper()
        config["loggers"]["keys"] = "root"

    try:
        logging.config.fileConfig(config, disable_existing_loggers=False)
    except KeyError:
        # config file does not configure logging, that's ok
        pass

    balance(config["pve"], wait=args.wait, dry=args.dry, exclude_names=args.exclude)


if __name__ == "__main__":
    main()
