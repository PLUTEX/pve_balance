from collections import namedtuple


VM = namedtuple("VM", ("id", "used_memory", "total_memory", "host"))
Migration = namedtuple("Migration", ("vm", "target_host"))


class Host:
    def __init__(self, name, used_memory, total_memory, vms):
        self.name = name
        self.used_memory = used_memory
        self.total_memory = total_memory
        self.vms = vms
        self.memory_imbalance = None

    def __repr__(self):
        return "Host(name={self.name!r})".format(self=self)
