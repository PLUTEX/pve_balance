from collections import namedtuple


VM = namedtuple('VM', ('id', 'memory'))
Migration = namedtuple('Migration', ('vm', 'target_host'))


class Host:
    def __init__(self, name, memory, vms):
        self.name = name
        self.memory = memory
        self.vms = vms
        self.memory_imbalance = None

    @property
    def used_memory(self):
        return sum(vm.memory for vm in self.vms)

    def __repr__(self):
        return 'Host(name={self.name}, memory={self.memory})'.format(self=self)
