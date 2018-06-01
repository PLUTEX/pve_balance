#! /usr/bin/env python3

import logging

from proxmoxer import ProxmoxAPI

from model import Host, VM
from algorithm import calculate_migrations


def main(pve_config):
    proxmox = ProxmoxAPI(**pve_config)

    hosts = []

    for node in proxmox.nodes.get():
        vms = []
        for vm in proxmox.nodes(node['node']).qemu.get():
            vms.append(VM(
                id=vm['vmid'],
                used_memory=vm['mem'],
                total_memory=vm['maxmem'],
                host=node['node'],
            ))
        hosts.append(Host(
            name=node['node'],
            used_memory=node['mem'],
            total_memory=node['maxmem'],
            vms=vms,
        ))

    for migration in calculate_migrations(hosts):
        print(migration)


if __name__ == '__main__':
    from configparser import ConfigParser
    config = ConfigParser()
    config.read('config.ini')
    logging.basicConfig(level=logging.INFO)

    main(config['pve'])
