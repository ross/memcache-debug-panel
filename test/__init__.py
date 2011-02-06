#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.DEBUG)

import unittest
import pylibmc
import memcache
import memcache_toolbar.panels.memcache

class TestCase(unittest.TestCase):

    def assertCall(self, call, expected_function, expected_args, base_message):
        self.assertTrue(call, base_message + ', no last call')
        self.assertEquals(call['function'], expected_function,
                base_message + ', last call function mis-match: %s != %s' %
                (expected_function, call['function']))
        self.assertEquals(call['args'], expected_args, base_message +
                ', args mis-match: %s != %s' % (expected_args, call['args']))
        self.assertTrue('start' in call, base_message + ', start missing')
        self.assertTrue('duration' in call, base_message + ', duration missing')

    def assertLastCall(self, expected_function, expected_args, base_message):
        self.assertCall(memcache_toolbar.panels.memcache.instance.last(),
                expected_function, expected_args, base_message)

    def assertLastCallRaised(self, expected_function, expected_args,
            base_message):
        call = memcache_toolbar.panels.memcache.instance.last()
        self.assertCall(call, expected_function, expected_args, base_message)
        self.assertTrue('exception' in call, base_message +
                ', did not throw an exception')

class TestPyLibMc(TestCase):

    def test_basic(self):
        client = pylibmc.Client(['127.0.0.1'], binary=True)
        client.behaviors = {'tcp_nodelay': True, 'ketama': True}

        # flush_all, first so we're in a clean state
        self.assertTrue(client.flush_all(), 'flush_all')
        self.assertLastCall('flush_all', None, 'initial flush')

        # set
        key = 'key'
        value = 'value'
        self.assertTrue(client.set(key, value), 'simple set')
        self.assertLastCall('set', key, 'simple set')
        # get
        self.assertEqual(client.get(key), value, 'simple get')
        self.assertLastCall('get', key, 'simple get')
        # set_multi
        multi = {'key1': 'value1', 'array': ['a1', 'a2'], 'bool': True}
        multi_keys = multi.keys()
        self.assertEqual(client.set_multi(multi), [], 'set multi')
        self.assertLastCall('set_multi', multi_keys, 'set_multi')
        # get_multi
        self.assertEqual(client.get_multi(multi_keys), multi, 'get_multi')
        self.assertLastCall('get_multi', multi_keys, 'get_multi')
        # add
        add = 'add'
        self.assertTrue(client.add(add, value), 'simple add, success')
        self.assertLastCall('add', add, 'simple add, success')
        self.assertFalse(client.add(add, value), 'simple add, exists')
        self.assertLastCall('add', add, 'simple add, exists')
        # replace
        self.assertTrue(client.replace(add, value), 'simple replace, exists')
        self.assertLastCall('replace', add, 'simple replace, exists')
        non_existent = 'non-existent'
        self.assertRaises(pylibmc.NotFound, client.replace, non_existent,
                value) # 'simple replace, non-existent raises'
        self.assertLastCallRaised('replace', non_existent,
                'simple replace, non-existent')
        # append
        self.assertTrue(client.append(key, value), 'simple append')
        self.assertLastCall('append', key, 'simple append, exists')
        empty = 'empty'
        self.assertFalse(client.append(empty, value), 'simple append, empty')
        self.assertLastCall('append', empty, 'simple append, empty')
        # prepend
        self.assertTrue(client.prepend(key, value), 'simple prepend')
        self.assertLastCall('prepend', key, 'simmple prepend, exists')
        self.assertFalse(client.prepend(empty, value), 'simple prepend, empty')
        self.assertLastCall('prepend', empty, 'simple prepend, empty')
        # incr
        incr = 'incr'
        self.assertRaises(pylibmc.NotFound, client.incr, non_existent)
                # , 'simple incr, non-existent')
        self.assertLastCallRaised('incr', non_existent,
                'simple incr, non-existent')
        count = 0
        self.assertTrue(client.set(incr, count), 'set initial incr')
        self.assertLastCall('set', incr, 'set initial incr')
        count += 1
        self.assertEquals(client.incr(incr), count, 'simple incr')
        self.assertLastCall('incr', incr, 'simple incr')
        # decr
        self.assertRaises(pylibmc.NotFound, client.decr, non_existent)
                # , 'simple decr, non-existent')
        self.assertLastCallRaised('decr', non_existent,
                'simple decr, non-existent')
        count -= 1
        self.assertEquals(client.decr(incr), count, 'simple decr')
        self.assertLastCall('decr', incr, 'simple decr')
        # delete
        self.assertTrue(client.delete(key), 'simple delete')
        self.assertLastCall('delete', key, 'simple delete')
        self.assertFalse(client.delete(non_existent),
                'simple delete, non-existent')
        self.assertLastCall('delete', non_existent,
                'simple delete, non-existent')
        # delete_multi (pylibmc implements this as foreach keys delete)
        n = memcache_toolbar.panels.memcache.instance.size()
        self.assertTrue(client.delete_multi(multi_keys), 'delete_multi')
        calls = memcache_toolbar.panels.memcache.instance.calls()
        # before + num_keys + the delete_multi
        self.assertEquals(n + len(multi_keys) + 1, len(calls),
                'delete multi call count')
        self.assertCall(calls[-4], 'delete_multi', multi_keys, 'delete_multi')
        for i, key in enumerate(multi_keys):
            self.assertCall(calls[-3 + i], 'delete', key,
                    'delete_multi, subsequent delete %d' % i)

        # flush again, this time make sure it works
        self.assertTrue(client.flush_all(), 'flush_all')
        self.assertLastCall('flush_all', None, 'flush_all')
        self.assertEquals(client.get(incr), None, 'flush worked')
        self.assertLastCall('get', incr, 'flush worked')

        self.assertEquals(26, memcache_toolbar.panels.memcache.instance.size(),
                'total number of calls')

        # test out the panel, mainly resetting
        panel = memcache_toolbar.panels.memcache.MemcachePanel()
        nav_subtitle = panel.nav_subtitle()
        self.assertEquals(nav_subtitle[0:2], '26', 'pylibmc panel.nav_subtitle')
        # reset things
        panel.process_request(None)
        nav_subtitle = panel.nav_subtitle()
        self.assertEquals(nav_subtitle, '0 calls',
                'pylibmc panel.nav_subtitle, post reset')

class TestMemcache(TestCase):

    def test_basic(self):
        client = memcache.Client(['127.0.0.1:11211'], debug=0)

        # flush_all, first so we're in a clean state
        client.flush_all()
        self.assertLastCall('flush_all', None, 'initial flush')

        # set
        key = 'key'
        value = 'value'
        self.assertTrue(client.set(key, value), 'simple set')
        self.assertLastCall('set', key, 'simple set')
        # get
        self.assertEqual(client.get(key), value, 'simple get')
        self.assertLastCall('get', key, 'simple get')
        # set_multi
        multi = {'key1': 'value1', 'array': ['a1', 'a2'], 'bool': True}
        multi_keys = multi.keys()
        self.assertEqual(client.set_multi(multi), [], 'set multi')
        self.assertLastCall('set_multi', multi_keys, 'set_multi')
        # get_multi
        self.assertEqual(client.get_multi(multi_keys), multi, 'get_multi')
        self.assertLastCall('get_multi', multi_keys, 'get_multi')
        # add
        add = 'add'
        self.assertTrue(client.add(add, value), 'simple add, success')
        self.assertLastCall('add', add, 'simple add, success')
        self.assertFalse(client.add(add, value), 'simple add, exists')
        self.assertLastCall('add', add, 'simple add, exists')
        # replace
        self.assertTrue(client.replace(add, value), 'simple replace, exists')
        self.assertLastCall('replace', add, 'simple replace, exists')
        non_existent = 'non-existent'
        self.assertRaises(pylibmc.NotFound, client.replace, non_existent,
                value) # 'simple replace, non-existent raises'
        self.assertLastCallRaised('replace', non_existent,
                'simple replace, non-existent')
        # append
        self.assertTrue(client.append(key, value), 'simple append')
        self.assertLastCall('append', key, 'simple append, exists')
        empty = 'empty'
        self.assertFalse(client.append(empty, value), 'simple append, empty')
        self.assertLastCall('append', empty, 'simple append, empty')
        # prepend
        self.assertTrue(client.prepend(key, value), 'simple prepend')
        self.assertLastCall('prepend', key, 'simmple prepend, exists')
        self.assertFalse(client.prepend(empty, value), 'simple prepend, empty')
        self.assertLastCall('prepend', empty, 'simple prepend, empty')
        # incr
        incr = 'incr'
        self.assertRaises(pylibmc.NotFound, client.incr, non_existent)
                # , 'simple incr, non-existent')
        self.assertLastCallRaised('incr', non_existent,
                'simple incr, non-existent')
        count = 0
        self.assertTrue(client.set(incr, count), 'set initial incr')
        self.assertLastCall('set', incr, 'set initial incr')
        count += 1
        self.assertEquals(client.incr(incr), count, 'simple incr')
        self.assertLastCall('incr', incr, 'simple incr')
        # decr
        self.assertRaises(pylibmc.NotFound, client.decr, non_existent)
                # , 'simple decr, non-existent')
        self.assertLastCallRaised('decr', non_existent,
                'simple decr, non-existent')
        count -= 1
        self.assertEquals(client.decr(incr), count, 'simple decr')
        self.assertLastCall('decr', incr, 'simple decr')
        # delete
        self.assertTrue(client.delete(key), 'simple delete')
        self.assertLastCall('delete', key, 'simple delete')
        self.assertFalse(client.delete(non_existent),
                'simple delete, non-existent')
        self.assertLastCall('delete', non_existent,
                'simple delete, non-existent')
        # delete_multi (pylibmc implements this as foreach keys delete)
        n = memcache_toolbar.panels.memcache.instance.size()
        self.assertTrue(client.delete_multi(multi_keys), 'delete_multi')
        calls = memcache_toolbar.panels.memcache.instance.calls()
        # before + num_keys + the delete_multi
        self.assertEquals(n + len(multi_keys) + 1, len(calls),
                'delete multi call count')
        self.assertCall(calls[-4], 'delete_multi', multi_keys, 'delete_multi')
        for i, key in enumerate(multi_keys):
            self.assertCall(calls[-3 + i], 'delete', key,
                    'delete_multi, subsequent delete %d' % i)

        # flush again, this time make sure it works
        self.assertTrue(client.flush_all(), 'flush_all')
        self.assertLastCall('flush_all', None, 'flush_all')
        self.assertEquals(client.get(incr), None, 'flush worked')
        self.assertLastCall('get', incr, 'flush worked')

        self.assertEquals(26, memcache_toolbar.panels.memcache.instance.size(),
                'total number of calls')

        # test out the panel, mainly resetting
        panel = memcache_toolbar.panels.memcache.MemcachePanel()
        nav_subtitle = panel.nav_subtitle()
        self.assertEquals(nav_subtitle[0:2], '26', 
                'memcache panel.nav_subtitle')
        # reset things
        panel.process_request(None)
        nav_subtitle = panel.nav_subtitle()
        self.assertEquals(nav_subtitle, '0 calls',
                'memcache panel.nav_subtitle, post reset')

if __name__ == '__main__':
    unittest.main()
