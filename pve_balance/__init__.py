from time import sleep

from proxmoxer import ProxmoxAPI

from .model import Host, VM
from .algorithm import calculate_migrations
from .helper import get_logger


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


def balance(pve_config, dry=False, wait=False, exclude_names=[]):
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

    if wait:
        while len(running) > 0:
            wait_for_tasks(proxmox, running)
