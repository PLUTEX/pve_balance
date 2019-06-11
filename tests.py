import unittest

from model import Host, VM, Migration
from algorithm import calculate_migrations


class TestCase1(unittest.TestCase):
    vm_sets = (
        (
            VM(1, 1024 ** 3, 1024 ** 3, ""),
            VM(2, 2 * 1024 ** 3, 2 * 1024 ** 3, ""),
        ),
        (
            VM(3, 4 * 1024 ** 3, 4 * 1024 ** 3, ""),
        ),
        (
            VM(4, 2 * 1024 ** 3, 2 * 1024 ** 3, ""),
        ),
    )

    def test_empty(self):
        self.assertEqual(calculate_migrations([]), [])

    def test_single_empty_host(self):
        hosts = [Host(
            name="empty",
            used_memory=0,
            total_memory=10 * 1024 ** 3,
            vms=[],
        )]
        self.assertEqual(calculate_migrations(hosts), [])

    def test_single_host(self):
        hosts = [Host(
            name="host1",
            used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
            total_memory=10 * 1024 ** 3,
            vms=self.vm_sets[0],
        )]
        self.assertEqual(calculate_migrations(hosts), [])

    def test_totally_imbalanced(self):
        hosts = [
            Host(
                name="host1",
                used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
                total_memory=10 * 1024 ** 3,
                vms=self.vm_sets[0],
            ),
            Host(
                name="host2",
                used_memory=0,
                total_memory=10 * 1024 ** 3,
                vms=[],
            ),
        ]
        self.assertEqual(
            calculate_migrations(hosts),
            [Migration(self.vm_sets[0][0], hosts[1].name)]
        )

    def test_little_imbalanced(self):
        hosts = [
            Host(
                name="host1",
                used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[0],
            ),
            Host(
                name="host2",
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
                name="host1",
                used_memory=sum(vm.used_memory for vm in self.vm_sets[0]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[0],
            ),
            Host(
                name="host2",
                used_memory=sum(vm.used_memory for vm in self.vm_sets[1]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[1],
            ),
            Host(
                name="host3",
                used_memory=sum(vm.used_memory for vm in self.vm_sets[2]),
                total_memory=20 * 1024 ** 3,
                vms=self.vm_sets[2],
            ),
        ]
        self.assertEqual(
            calculate_migrations(hosts, exclude=[hosts[1]]),
            [
                Migration(self.vm_sets[1][0], hosts[2].name),
                Migration(self.vm_sets[2][0], hosts[0].name),
            ]
        )


class TestCase2(unittest.TestCase):
    """Real-life test data"""

    hosts = [
        Host(name="1", used_memory=5577834496, total_memory=8336060416, vms=[
            VM(
                id="10",
                used_memory=3447648677,
                total_memory=4294967296,
                host="1"),
            VM(
                id="11",
                used_memory=190052422,
                total_memory=536870912,
                host="1"),
        ]),
        Host(name="2", used_memory=11513454592, total_memory=16810565632, vms=[
            VM(
                id="20",
                used_memory=5268212597,
                total_memory=6442450944,
                host="2"),
            VM(
                id="21",
                used_memory=517167212,
                total_memory=1073741824,
                host="2"),
            VM(
                id="22",
                used_memory=539252463,
                total_memory=1073741824,
                host="2"),
            VM(
                id="23",
                used_memory=1381256319,
                total_memory=2147483648,
                host="2"),
        ]),
        Host(name="3", used_memory=47736459264, total_memory=75960635392, vms=[
            VM(
                id="30",
                used_memory=537456743,
                total_memory=1073741824,
                host="3"),
            VM(
                id="31",
                used_memory=3365387199,
                total_memory=4294967296,
                host="3"),
            VM(
                id="32",
                used_memory=1389582985,
                total_memory=2147483648,
                host="3"),
            VM(
                id="33",
                used_memory=1390639531,
                total_memory=2147483648,
                host="3"),
            VM(
                id="34",
                used_memory=24402832870,
                total_memory=25769803776,
                host="3"),
            VM(
                id="35",
                used_memory=6073533399,
                total_memory=8589934592,
                host="3"),
            VM(
                id="36",
                used_memory=554643452,
                total_memory=1073741824,
                host="3"),
            VM(
                id="37",
                used_memory=523895362,
                total_memory=1073741824,
                host="3"),
        ]),
        Host(name="4", used_memory=18576535552, total_memory=33702326272, vms=[
            VM(
                id="40",
                used_memory=11545060932,
                total_memory=12884901888,
                host="4"),
            VM(
                id="41",
                used_memory=3285360214,
                total_memory=4294967296,
                host="4"),
        ]),
        Host(name="5", used_memory=17184206848, total_memory=33702330368, vms=[
            VM(
                id="50",
                used_memory=195475157,
                total_memory=536870912,
                host="5"),
            VM(
                id="51",
                used_memory=288758423,
                total_memory=1073741824,
                host="5"),
            VM(
                id="52",
                used_memory=7597993777,
                total_memory=8589934592,
                host="5"),
            VM(
                id="53",
                used_memory=108632361,
                total_memory=1073741824,
                host="5"),
            VM(
                id="54",
                used_memory=517418703,
                total_memory=1073741824,
                host="5"),
            VM(
                id="55",
                used_memory=1463342765,
                total_memory=2147483648,
                host="5"),
            VM(
                id="56",
                used_memory=1423234506,
                total_memory=2147483648,
                host="5"),
        ]),
        Host(name="6", used_memory=36207448064, total_memory=67501617152, vms=[
            VM(
                id="60",
                used_memory=1304373103,
                total_memory=2147483648,
                host="6"),
            VM(
                id="61",
                used_memory=3326296408,
                total_memory=4294967296,
                host="6"),
            VM(
                id="62",
                used_memory=7323900185,
                total_memory=8589934592,
                host="6"),
            VM(
                id="63",
                used_memory=3180866707,
                total_memory=4294967296,
                host="6"),
            VM(
                id="64",
                used_memory=553806610,
                total_memory=1073741824,
                host="6"),
            VM(
                id="65",
                used_memory=517243773,
                total_memory=1073741824,
                host="6"),
            VM(
                id="66",
                used_memory=3210596596,
                total_memory=4294967296,
                host="6"),
            VM(
                id="67",
                used_memory=1447047938,
                total_memory=2147483648,
                host="6"),
            VM(
                id="68",
                used_memory=3159483370,
                total_memory=4294967296,
                host="6"),
            VM(
                id="69",
                used_memory=524345612,
                total_memory=1073741824,
                host="6"),
        ]),
        Host(name="7", used_memory=20850761728, total_memory=42171383808, vms=[
            VM(
                id="70",
                used_memory=1373962012,
                total_memory=2147483648,
                host="7"),
            VM(
                id="71",
                used_memory=575198135,
                total_memory=1073741824,
                host="7"),
            VM(
                id="72",
                used_memory=3718019040,
                total_memory=8589934592,
                host="7"),
            VM(
                id="73",
                used_memory=1437787148,
                total_memory=2147483648,
                host="7"),
            VM(
                id="74",
                used_memory=752788754,
                total_memory=8589934592,
                host="7"),
            VM(
                id="75",
                used_memory=543499649,
                total_memory=1073741824,
                host="7"),
            VM(
                id="76",
                used_memory=539375148,
                total_memory=1073741824,
                host="7"),
            VM(
                id="77",
                used_memory=1422989723,
                total_memory=2147483648,
                host="7"),
            VM(
                id="78",
                used_memory=3287090290,
                total_memory=4294967296,
                host="7"),
            VM(
                id="79",
                used_memory=952316977,
                total_memory=1610612736,
                host="7"),
        ]),
        Host(name="8", used_memory=18705526784, total_memory=33702330368, vms=[
            VM(
                id="80",
                used_memory=538191995,
                total_memory=1073741824,
                host="8"),
            VM(
                id="81",
                used_memory=531513577,
                total_memory=1073741824,
                host="8"),
            VM(
                id="82",
                used_memory=537768925,
                total_memory=1073741824,
                host="8"),
            VM(
                id="83",
                used_memory=555081242,
                total_memory=1073741824,
                host="8"),
            VM(
                id="84",
                used_memory=7387446591,
                total_memory=8589934592,
                host="8"),
            VM(
                id="85",
                used_memory=3414347823,
                total_memory=4294967296,
                host="8"),
        ]),
        Host(name="9", used_memory=38379773952, total_memory=67517632512, vms=[
            VM(
                id="90",
                used_memory=3155109231,
                total_memory=4294967296,
                host="9"),
            VM(
                id="91",
                used_memory=3363702409,
                total_memory=4294967296,
                host="9"),
            VM(
                id="92",
                used_memory=1368483645,
                total_memory=2147483648,
                host="9"),
            VM(
                id="93",
                used_memory=1910461708,
                total_memory=4294967296,
                host="9"),
            VM(
                id="94",
                used_memory=1361888310,
                total_memory=2147483648,
                host="9"),
            VM(
                id="95",
                used_memory=532955442,
                total_memory=1073741824,
                host="9"),
            VM(
                id="96",
                used_memory=534007219,
                total_memory=1073741824,
                host="9"),
            VM(
                id="97",
                used_memory=3099406894,
                total_memory=4294967296,
                host="9"),
            VM(
                id="98",
                used_memory=7380403436,
                total_memory=8589934592,
                host="9"),
            VM(
                id="99",
                used_memory=3305062677,
                total_memory=4294967296,
                host="9"),
        ]),
        Host(name="a", used_memory=13403484160, total_memory=25247420416, vms=[
            VM(
                id="a0",
                used_memory=3221945788,
                total_memory=4294967296,
                host="a"),
            VM(
                id="a1",
                used_memory=553793774,
                total_memory=1073741824,
                host="a"),
            VM(
                id="a2",
                used_memory=3377389963,
                total_memory=4294967296,
                host="a"),
            VM(
                id="a3",
                used_memory=531185564,
                total_memory=1073741824,
                host="a"),
            VM(
                id="a4",
                used_memory=538601985,
                total_memory=1073741824,
                host="a"),
        ]),
        Host(name="b", used_memory=40388665344, total_memory=75960639488, vms=[
            VM(
                id="b0",
                used_memory=538192584,
                total_memory=1073741824,
                host="b"),
            VM(
                id="b1",
                used_memory=1411996281,
                total_memory=2147483648,
                host="b"),
            VM(
                id="b2",
                used_memory=199685682,
                total_memory=536870912,
                host="b"),
            VM(
                id="b3",
                used_memory=1371761367,
                total_memory=2147483648,
                host="b"),
            VM(
                id="b4",
                used_memory=535095282,
                total_memory=1073741824,
                host="b"),
            VM(
                id="b5",
                used_memory=3230251060,
                total_memory=4294967296,
                host="b"),
            VM(
                id="b6",
                used_memory=3259391242,
                total_memory=4294967296,
                host="b"),
            VM(
                id="b7",
                used_memory=15715654848,
                total_memory=17179869184,
                host="b"),
            VM(
                id="b8",
                used_memory=3291853877,
                total_memory=4294967296,
                host="b"),
        ]),
        Host(name="c", used_memory=2987741184, total_memory=67538604032, vms=[
        ]),
    ]

    def test_idempotence(self):
        hosts = list(self.hosts)
        migrations = calculate_migrations(hosts)
        for migration in migrations:
            source_host = next(
                host for host in hosts
                if host.name == migration.vm.host
            )
            source_host.vms.remove(migration.vm)
            source_host.used_memory -= migration.vm.used_memory
            target_host = next(
                host for host in hosts
                if host.name == migration.target_host
            )
            target_host.vms.append(
                VM(*migration.vm[:-1], host=migration.target_host)
            )
            target_host.used_memory += migration.vm.used_memory
        calculate_migrations(hosts)
        self.assertEqual(calculate_migrations(hosts), [])


if __name__ == "__main__":
    unittest.main()
