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


def main(pve_config, dry=False, exclude_names=[]):
    proxmox = ProxmoxAPI(**pve_config)

    hosts = []
    exclude = []

    for node in proxmox.nodes.get():
        vms = []
        for vm in proxmox.nodes(node["node"]).qemu.get(full=1):
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
            logger.info(
                "Waiting for completion of one of {} tasks",
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


if __name__ == "__main__":
    from configparser import ConfigParser
    import argparse

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

    config = ConfigParser()
    config.read("config.ini")

    parser = argparse.ArgumentParser(
        description="Balance VMs in a Proxmox Virtual Environment cluster."
    )
    parser.add_argument("host")
    parser.add_argument("--loglevel", metavar="LEVEL", type=loglevel_to_int)
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()

    config["pve"]["host"] = args.host

    import yaml
    with open("logging.yml") as f:
        log_config = yaml.safe_load(f)
    if args.loglevel:
        log_config["handlers"]["console"]["level"] = args.loglevel
        log_config["loggers"] = {}
    logging.config.dictConfig(log_config)

    main(config["pve"], dry=args.dry, exclude_names=args.exclude)
