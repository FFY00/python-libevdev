import unittest
import ctypes
from libevdev import *

# Note: these tests test for the correct functioning of the python bindings,
# not of libevdev underneath. Some ranges are hardcoded for simplicity, e.g.
# if properties 1-4 work the others will work too if libevdev works
# correctly

class TestNameConversion(unittest.TestCase):
    def test_prop_name(self):
        l = Libevdev()
        name = l.property_name(0)
        self.assertEqual(name, "INPUT_PROP_POINTER")

        prevname = None
        for i in range(0, 5):
            name = l.property_name(i)
            self.assertIsNotNone(name)
            self.assertTrue(name.startswith("INPUT_PROP_"))
            self.assertNotEqual(prevname, name)
            prevname = name

    def test_prop_name_invalid(self):
        l = Libevdev()
        name = l.property_name(-1)
        self.assertIsNone(name)
        name = l.property_name(100)
        self.assertIsNone(name)
        with self.assertRaises(ctypes.ArgumentError):
            name = l.property_name("foo")

    def test_type_name(self):
        l = Libevdev()
        name = l.event_name(1)
        self.assertEqual(name, "EV_KEY")

        prevname = None
        for i in range(0, 5):
            name = l.event_name(i)
            self.assertIsNotNone(name)
            self.assertTrue(name.startswith("EV_"))
            self.assertNotEqual(prevname, name)
            prename = name

    def test_type_name_invalid(self):
        l = Libevdev()
        name = l.event_name(-1)
        self.assertIsNone(name)
        name = l.event_name(100)
        self.assertIsNone(name)
        with self.assertRaises(ctypes.ArgumentError):
            name = l.event_name("foo")

    def test_code_name(self):
        l = Libevdev()
        name = l.event_name(0, 0)
        self.assertEqual(name, "SYN_REPORT")

        name = l.event_name(1, 1)
        self.assertEqual(name, "KEY_ESC")

    def test_code_name_invalid(self):
        l = Libevdev()
        name = l.event_name(0, 1000)
        self.assertIsNone(name)
        name = l.event_name(0, -1)
        self.assertIsNone(name)
        with self.assertRaises(ctypes.ArgumentError):
            name = l.event_name(0, "foo")

    def test_type_value(self):
        l = Libevdev()
        v = l.event_value("EV_REL")
        self.assertEqual(v, 2)

    def test_type_value_invalid(self):
        l = Libevdev()
        v = l.event_value("foo")
        self.assertIsNone(v)
        with self.assertRaises(ctypes.ArgumentError):
            v = l.event_value(0)

    def test_code_value(self):
        l = Libevdev()
        v = l.event_value("EV_REL", "REL_Y")
        self.assertEqual(v, 1)

        v = l.event_value(0, "SYN_DROPPED")
        self.assertEqual(v, 3)

    def test_code_value_invalid(self):
        l = Libevdev()
        v = l.event_value("EV_REL", "KEY_ESC")
        self.assertIsNone(v)


class TestLibevdevDevice(unittest.TestCase):
    def test_ctx_init(self):
        l = Libevdev()
        del l

    def test_set_get_name(self):
        l = Libevdev()
        name = l.name
        self.assertEqual(name, '')

        l.name = "foo"
        name = l.name
        self.assertEqual(name, "foo")

        l.name = None
        name = l.name
        self.assertEqual(name, "")

    def test_set_get_uniq(self):
        l = Libevdev()
        uniq = l.uniq
        self.assertIsNone(uniq)

        l.uniq = "foo"
        uniq = l.uniq
        self.assertEqual(uniq, "foo")

        # libevdev issue: phys may be NULL (unlike the name) but we can't
        # set it to NULL
        l.uniq = None
        uniq = l.uniq
        self.assertEqual(uniq, "")

    def test_set_get_phys(self):
        l = Libevdev()
        phys = l.phys
        self.assertIsNone(phys)

        l.phys = "foo"
        phys = l.phys
        self.assertEqual(phys, "foo")

        # libevdev issue: phys may be NULL (unlike the name) but we can't
        # set it to NULL
        l.phys = None
        phys = l.phys
        self.assertEqual(phys, "")

    def test_get_driver_version(self):
        l = Libevdev()
        v = l.driver_version
        self.assertEqual(v, 0)
        # we can't set this, nothing else we can test

    def test_set_get_id(self):
        l = Libevdev()
        id = l.id
        self.assertEqual(id["bustype"], 0)
        self.assertEqual(id["vendor"], 0)
        self.assertEqual(id["product"], 0)
        self.assertEqual(id["version"], 0)

        id["bustype"] = 1
        id["vendor"] = 2
        id["product"] = 3
        id["version"] = 4

        l.id = id
        id = l.id
        self.assertEqual(id["bustype"], 1)
        self.assertEqual(id["vendor"], 2)
        self.assertEqual(id["product"], 3)
        self.assertEqual(id["version"], 4)

        del id["bustype"]
        del id["vendor"]
        del id["product"]
        id["version"] = 5

        l.id = id
        id = l.id
        self.assertEqual(id["bustype"], 1)
        self.assertEqual(id["vendor"], 2)
        self.assertEqual(id["product"], 3)
        self.assertEqual(id["version"], 5)

if __name__ == '__main__':
    unittest.main()

