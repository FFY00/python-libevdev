# -*- coding: latin-1 -*-
# Copyright © 2017 Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice (including the next
# paragraph) shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import unittest

import libevdev
from libevdev import evbit, propbit, InputEvent, Device, InvalidFileError, InvalidArgumentException

def is_root():
    return os.getuid() == 0

class TestDevice(unittest.TestCase):
    def test_device_empty(self):
        d = libevdev.Device()
        id = {'bustype': 0, 'vendor': 0, 'product': 0, 'version': 0}
        syns = { libevdev.EV_SYN : libevdev.EV_SYN.codes }

        self.assertEqual(d.name, '')
        self.assertEqual(d.id, id)
        self.assertIsNone(d.fd)
        self.assertIsNone(d.phys)
        self.assertIsNone(d.uniq)
        self.assertEqual(d.driver_version, 0)
        self.assertIsNone(d.syspath)
        self.assertIsNone(d.devnode)
        self.assertEqual(d.evbits, syns)
        self.assertEqual(d.properties, [])

        for t in libevdev.types:
            if t == libevdev.EV_SYN:
                continue

            self.assertFalse(d.has_event(t))

            for c in t.codes:
                self.assertFalse(d.has_event(c))
                self.assertIsNone(d.event_value(c))

                d.disable(c) # noop

            d.disable(t) # noop

        for p in libevdev.props:
            self.assertFalse(d.has_property(p))

        self.assertIsNone(d.num_slots)
        self.assertIsNone(d.current_slot)

        for c in libevdev.EV_ABS.codes:
            self.assertIsNone(d.absinfo(c))

        self.assertEqual([e for e in d.events()], [])
        self.assertEqual([e for e in d.sync()], [])

        with self.assertRaises(libevdev.InvalidArgumentException):
            d.slot_value(0, libevdev.EV_ABS.ABS_MT_POSITION_X)

    def test_device_name(self):
        d = libevdev.Device()
        d.name = 'test device'
        self.assertEqual(d.name, 'test device')

    def test_device_id(self):
        d = libevdev.Device()
        id = {'bustype': 1, 'vendor': 2, 'product': 3, 'version': 4}
        d.id = id
        self.assertEqual(d.id, id)

        d.id = {'vendor': 3, 'product': 4, 'version': 5}
        id = {'bustype': 1, 'vendor': 3, 'product': 4, 'version': 5}
        self.assertEqual(d.id, id)

        d.id = {'bustype': 8, 'product': 5, 'version': 6}
        id = {'bustype': 8, 'vendor': 3, 'product': 5, 'version': 6}
        self.assertEqual(d.id, id)

        d.id = {'bustype': 8, 'vendor': 9, 'version': 10}
        id = {'bustype': 8, 'vendor': 9, 'product': 5, 'version': 10}
        self.assertEqual(d.id, id)

        d.id = {'bustype': 8, 'vendor': 9, 'product': 12}
        id = {'bustype': 8, 'vendor': 9, 'product': 12, 'version': 10}
        self.assertEqual(d.id, id)

    def test_device_phys(self):
        d = libevdev.Device()
        d.phys = 'foo'
        self.assertEqual(d.phys, 'foo')

        d.phys = None
        self.assertIsNone(d.phys)

    def test_device_uniq(self):
        d = libevdev.Device()
        d.uniq = 'bar'
        self.assertEqual(d.uniq, 'bar')

        d.uniq = None
        self.assertIsNone(d.uniq)

    def test_driver_version(self):
        d = libevdev.Device()
        # read-only
        with self.assertRaises(AttributeError):
            d.driver_version = 1

    def test_garbage_fd(self):
        with self.assertRaises(InvalidFileError):
            libevdev.Device(fd=1)

        with self.assertRaises(InvalidFileError):
            d = libevdev.Device()
            d.fd = 2

    @unittest.skipUnless(is_root(), 'Test requires root')
    def test_fd_on_init(self):
        fd = open('/dev/input/event0', 'rb')
        d = libevdev.Device(fd)
        self.assertEqual(d.fd, fd)

    @unittest.skipUnless(is_root(), 'Test requires root')
    def test_fd_too_late(self):
        fd = open('/dev/input/event0', 'rb')
        d = libevdev.Device()
        with self.assertRaises(InvalidFileError):
            d.fd = fd

    @unittest.skipUnless(is_root(), 'Test requires root')
    def test_fd_change(self):
        fd1 = open('/dev/input/event0', 'rb')
        fd2 = open('/dev/input/event1', 'rb')
        d = libevdev.Device(fd1)
        self.assertEqual(d.fd, fd1)
        d.fd = fd2
        self.assertEqual(d.fd, fd2)

    @unittest.skipUnless(is_root(), 'Test requires root')
    def test_has_bits(self):
        fd = open('/dev/input/event0', 'rb')
        d = libevdev.Device(fd)
        bits = d.evbits

        # assume at least 2 event types
        self.assertGreater(len(bits.keys()), 1)

        for t, cs in bits.items():
            if t == libevdev.EV_SYN:
                continue

            # assume at least one code
            self.assertGreater(len(cs), 0)

    def test_set_bits(self):
        d = libevdev.Device()
        # read-only
        with self.assertRaises(AttributeError):
            d.evbits = {}

    def test_bits_change_after_enable(self):
        d = libevdev.Device()
        bits = d.evbits
        self.assertIn(libevdev.EV_SYN, bits)
        self.assertNotIn(libevdev.EV_REL, bits)

        d.enable(libevdev.EV_REL.REL_X)
        d.enable(libevdev.EV_REL.REL_Y)

        bits = d.evbits
        self.assertIn(libevdev.EV_SYN, bits)
        self.assertIn(libevdev.EV_REL, bits)
        self.assertNotIn(libevdev.EV_ABS, bits)
        self.assertNotIn(libevdev.EV_KEY, bits)

        self.assertIn(libevdev.EV_REL.REL_X, bits[libevdev.EV_REL])
        self.assertIn(libevdev.EV_REL.REL_Y, bits[libevdev.EV_REL])

    def test_bits_change_after_disable(self):
        d = libevdev.Device()
        d.enable(libevdev.EV_REL.REL_X)
        d.enable(libevdev.EV_REL.REL_Y)
        d.enable(libevdev.EV_KEY.KEY_A)
        d.enable(libevdev.EV_KEY.KEY_B)

        bits = d.evbits
        self.assertIn(libevdev.EV_SYN, bits)
        self.assertIn(libevdev.EV_REL, bits)
        self.assertIn(libevdev.EV_KEY, bits)
        self.assertNotIn(libevdev.EV_ABS, bits)
        self.assertIn(libevdev.EV_REL.REL_X, bits[libevdev.EV_REL])
        self.assertIn(libevdev.EV_REL.REL_Y, bits[libevdev.EV_REL])
        self.assertIn(libevdev.EV_KEY.KEY_A, bits[libevdev.EV_KEY])
        self.assertIn(libevdev.EV_KEY.KEY_B, bits[libevdev.EV_KEY])

        d.disable(libevdev.EV_REL.REL_Y)
        d.disable(libevdev.EV_KEY)
        bits = d.evbits
        self.assertNotIn(libevdev.EV_KEY, bits)
        self.assertIn(libevdev.EV_REL, bits)
        self.assertIn(libevdev.EV_REL.REL_X, bits[libevdev.EV_REL])
        self.assertNotIn(libevdev.EV_REL.REL_Y, bits[libevdev.EV_REL])

    def test_properties(self):
        d = libevdev.Device()
        self.assertEqual(d.properties, [])
        for p in libevdev.props:
            self.assertFalse(d.has_property(p))

        props = sorted([libevdev.INPUT_PROP_BUTTONPAD, libevdev.INPUT_PROP_DIRECT])

        for p in props:
            d.enable(p)

        self.assertEqual(d.properties, props)
        for p in libevdev.props:
            if not p in props:
                self.assertFalse(d.has_property(p))
            else:
                self.assertTrue(d.has_property(p))

        with self.assertRaises(NotImplementedError):
            d.disable(libevdev.INPUT_PROP_BUTTONPAD)

    def test_has_event(self):
        d = libevdev.Device()

        d.enable(libevdev.EV_REL.REL_X)
        d.enable(libevdev.EV_REL.REL_Y)
        d.enable(libevdev.EV_KEY.KEY_A)
        d.enable(libevdev.EV_KEY.KEY_B)

        self.assertTrue(d.has_event(libevdev.EV_REL))
        self.assertTrue(d.has_event(libevdev.EV_REL.REL_X))
        self.assertTrue(d.has_event(libevdev.EV_REL.REL_Y))
        self.assertFalse(d.has_event(libevdev.EV_REL.REL_Z))

        self.assertTrue(d.has_event(libevdev.EV_KEY))
        self.assertTrue(d.has_event(libevdev.EV_KEY.KEY_A))
        self.assertTrue(d.has_event(libevdev.EV_KEY.KEY_B))
        self.assertFalse(d.has_event(libevdev.EV_KEY.KEY_C))

        self.assertFalse(d.has_event(libevdev.EV_ABS))

    def test_enable_abs(self):
        d = libevdev.Device()
        with self.assertRaises(InvalidArgumentException):
            d.enable(libevdev.EV_ABS.ABS_X)

    @unittest.skipUnless(is_root(), 'Test requires root')
    def test_uinput_empty(self):
        d = libevdev.Device()
        with self.assertRaises(OSError):
            d.create()
