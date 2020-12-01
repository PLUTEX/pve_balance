# PVE Balance

Automatically balance VMs in a [Proxmox Virtual Environment][PVE] cluster.

[PVE]: https://proxmox.com/en/proxmox-ve

## Configuration

Copy the `pve-balance.sample.ini` to one of `~/.config/pve-balance.ini`,
`/etc/pve-balance.ini` or `./pve-balance.ini` and enter your user credentials.

## Usage

```
$ pve_balance --help
usage: pve_balance [-h] [--exclude EXCLUDE] [--dry] [--wait]
                   [--loglevel LEVEL]
                   host

Balance VMs in a Proxmox Virtual Environment cluster.

positional arguments:
  host

optional arguments:
  -h, --help         show this help message and exit
  --exclude EXCLUDE  Exclude these cluster nodes from the target calculations.
                     This will migrate all VMs from these nodes onto others
                     and not migrate any VMs onto these nodes.
  --dry              Just calculate the migrations, but don't execute them
  --wait             Wait for all migrations to finish before exiting
  --loglevel LEVEL
```

## Algorithm

The algorithm uses memory usage as its sole criterion for balance.

It first sorts the cluster hosts by memory usage and then tries to migrate VMs
from the most used host to the least used. It tries to minimize migrations per
host by first migrating the VM that brings the source host closest to the
average cluster memory usage.

To watch the algorithm's work, you can pass the arguments `--dry --loglevel
debug` to make it print every step it takes and not perform any actions.
