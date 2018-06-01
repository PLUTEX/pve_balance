import unittest

from model import Host, VM, Migration
from algorithm import calculate_migrations


class TestCase1(unittest.TestCase):
    vm_sets = (
        (VM(1, 1024 ** 3), VM(2, 2 * 1024 ** 3)),
        (VM(3, 4 * 1024 ** 3),),
        (VM(4, 2 * 1024 ** 3),),
    )

    def test_empty(self):
        self.assertEqual(calculate_migrations([]), [])

    def test_single_empty_host(self):
        hosts = [Host('empty', 10 * 1024 ** 3, [])]
        self.assertEqual(calculate_migrations(hosts), [])

    def test_single_host(self):
        hosts = [Host('host1', 10 * 1024 ** 3, self.vm_sets[0])]
        self.assertEqual(calculate_migrations(hosts), [])

    def test_totally_imbalanced(self):
        hosts = [
            Host('host1', 10 * 1024 ** 3, self.vm_sets[0]),
            Host('host2', 10 * 1024 ** 3, []),
        ]
        self.assertEqual(
            calculate_migrations(hosts),
            [Migration(self.vm_sets[0][0], hosts[1])]
        )

    def test_little_imbalanced(self):
        hosts = [
            Host('host1', 20 * 1024 ** 3, self.vm_sets[0]),
            Host('host1', 10 * 1024 ** 3, self.vm_sets[1]),
        ]
        self.assertEqual(
            calculate_migrations(hosts),
            []
        )

    def test_migrate_empty(self):
        hosts = [
            Host('host1', 20 * 1024 ** 3, self.vm_sets[0]),
            Host('host2', 20 * 1024 ** 3, self.vm_sets[1]),
            Host('host3', 20 * 1024 ** 3, self.vm_sets[2]),
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
