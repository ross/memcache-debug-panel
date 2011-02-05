#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.DEBUG)

import unittest
import pylibmc
import sys
import memcache_toolbar.panels

class TestPyLibMc(unittest.TestCase):

    def test_basic(self):
        client = pylibmc.Client(['127.0.0.1'], binary=True)
        client.behaviors = {'tcp_nodelay': True, 'ketama': True}

        # flush_all, first so we're in a clean state
        self.assertTrue(client.flush_all(), 'flush_all')

        # set
        key = 'key'
        value = 'value'
        self.assertTrue(client.set(key, value), 'simple set')
        # get
        self.assertEqual(client.get(key), value, 'simple get')
        multi = {'key1': 'value1', 'array': ['a1', 'a2'], 'bool': True}
        # set_multi
        self.assertEqual(client.set_multi(multi), [], 'set multi')
        # get_multi
        self.assertEqual(client.get_multi(multi.keys()), multi, 'get multi')
        # add
        add = 'add'
        self.assertTrue(client.add(add, value), 'simple add, success')
        self.assertFalse(client.add(add, value), 'simple add, exists')
        # replace
        self.assertTrue(client.replace(add, value), 'simple replace, exists')
        self.assertRaises(pylibmc.NotFound, client.replace, 'non-existent',
                value) # 'simple replace, non-existent raises'
        # append
        self.assertTrue(client.append(key, value), 'simple append')
        # prepend
        self.assertTrue(client.prepend(key, value), 'simple prepend')
        # incr
        incr = 'incr'
        count = 0
        self.assertTrue(client.set(incr, count), 'set initial incr')
        count += 1
        self.assertEquals(client.incr(incr), count, 'simple incr')
        # decr
        count -= 1
        self.assertEquals(client.decr(incr), count, 'simple decr')
        # delete
        self.assertTrue(client.delete(key), 'simple delete')
        # delete_multi
        self.assertTrue(client.delete_multi(multi.keys()), 'delete multi')
        # flush again, this time make sure it works
        self.assertTrue(client.flush_all(), 'flush_all')
        self.assertEquals(client.get(incr), None, 'flush worked')



if __name__ == '__main__':
    unittest.main()
