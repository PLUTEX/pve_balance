#! /usr/bin/env python3

import logging
import logging.config
from time import sleep

from proxmoxer import ProxmoxAPI

from model import Host, VM
from algorithm import calculate_migrations
from helper import get_logger


logger = get_logger(__name__)


def hosts_in_migrations(migrations):
    yield from (migration.vm.host for migration in migrations)
    yield from (migration.target_host for migration in migrations)


def wait_for_tasks(proxmox, running):
    logger.info(
        "Waiting for completion of {} tasks",
        len(running),
    )

    num_running = len(running)
    while len(running) == num_running:
        for task in proxmox.cluster.tasks.get():
            if "endtime" in task:
                try:
                    del running[task["upid"]]
                except KeyError:
                    pass
        if len(running) == num_running:
            sleep(1)


def main(pve_config, dry=False, wait=False, exclude_names=[]):
    proxmox = ProxmoxAPI(**pve_config)

    hosts = []
    exclude = []

    for node in proxmox.nodes.get():
        vms = []
        for vm in proxmox.nodes(node["node"]).qemu.get(full=1):
            if vm["status"] != "running":
                continue

            vms.append(VM(
                id=vm["vmid"],
                used_memory=vm["mem"],
                total_memory=vm["maxmem"],
                host=node["node"],
            ))
        hosts.append(Host(
            name=node["node"],
            used_memory=node["mem"],
            total_memory=node["maxmem"],
            vms=vms,
        ))
        if node["node"] in exclude_names:
            exclude.append(hosts[-1])

    logger.debug("Starting to calculate migrations")
    migrations = calculate_migrations(hosts, exclude)

    if dry:
        logger.info("Terminating due to dry mode.")
        return

    running = {}
    while migrations:
        migrating_hosts = set(hosts_in_migrations(running.values()))
        for i, migration in enumerate(migrations):
            busy_hosts = \
                {migration.vm.host, migration.target_host} & migrating_hosts
            if busy_hosts:
                logger.debug(
                    "Postponing migration of VM {0.vm.id} , because {1} is "
                    "busy",
                    migration,
                    tuple(busy_hosts)[0],
                )
                continue

            logger.info(
                "Migrating VM {0.vm.id} ({0.vm.used_memory!b}) from host "
                "{0.vm.host} to host {0.target_host}.",
                migration,
            )

            vm = migration.vm
            task = proxmox.nodes(vm.host).qemu(vm.id).migrate.post(**{
                "target": migration.target_host,
                "online": 1,
                "with-local-disks": 1,
            })
            del vm

            running[task] = migration
            del migrations[i]
            break
        else:
            # we iterated through the non-empty list of remaining migrations,
            # meaning that all remaining migrations are currently blocked by
            # running migrations
            wait_for_tasks(proxmox, running)


if __name__ == "__main__":
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
        os.path.join(base, 'promo-balance.ini')
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

    logging.config.fileConfig(config, disable_existing_loggers=False)

    main(config["pve"], dry=args.dry, exclude_names=args.exclude)
