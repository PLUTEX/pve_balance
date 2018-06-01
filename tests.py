import unittest

from model import Host, VM, Migration
from algorithm import calculate_migrations


class TestCase1(unittest.TestCase):
    vm_sets = (
        (
            VM(1, 1024 ** 3, 1024 ** 3, ''),
            VM(2, 2 * 1024 ** 3, 2 * 1024 ** 3, ''),
        ),
        (
            VM(3, 4 * 1024 ** 3, 4 * 1024 ** 3, ''),
        ),
        (
            VM(4, 2 * 1024 ** 3, 2 * 1024 ** 3, ''),
        ),
    )

    def test_empty(self):
        self.assertEqual(calculate_migrations([]), [])

    def test_single_empty_host(self):
        hosts = [Host(
            name='empty',
            used_memory=0,
            total_memory=10 * 1024 ** 3,
            vms=[],
        )]
        self.assertEqual(calculate_migrations(hosts), [])

    def test_single_host(self):
        hosts = [Host(
            name='host1',
            used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
            total_memory=10 * 1024 ** 3,
            vms=self.vm_sets[0],
        )]
        self.assertEqual(calculate_migrations(hosts), [])

    def test_totally_imbalanced(self):
        hosts = [
            Host(
                name='host1',
                used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
                total_memory=10 * 1024 ** 3,
                vms=self.vm_sets[0],
            ),
            Host(
                name='host2',
                used_memory=0,
                total_memory=10 * 1024 ** 3,
                vms=[],
            ),
        ]
        self.assertEqual(
            calculate_migrations(hosts),
            [Migration(self.vm_sets[0][0], hosts[1])]
        )

    def test_little_imbalanced(self):
        hosts = [
            Host(
                name='host1',
                used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[0],
            ),
            Host(
                name='host2',
                used_memory=sum(vm.used_memory for vm in self.vm_sets[1]),
                total_memory=10 * 1024 ** 3,
                vms=self.vm_sets[1],
            ),
        ]
        self.assertEqual(
            calculate_migrations(hosts),
            []
        )

    def test_migrate_empty(self):
        hosts = [
            Host(
                name='host1',
                used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[0],
            ),
            Host(
                name='host2',
                used_memory=sum(vm.used_memory for vm in self.vm_sets[1]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[1],
            ),
            Host(
                name='host3',
                used_memory=sum(vm.used_memory for vm in self.vm_sets[2]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[2],
            ),
        ]
        self.assertEqual(
            calculate_migrations(hosts, exclude=[hosts[1]]),
            [
                Migration(self.vm_sets[1][0], hosts[2]),
                Migration(self.vm_sets[2][0], hosts[0]),
            ]
        )


if __name__ == '__main__':
    unittest.main()
