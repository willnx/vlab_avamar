# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in tasks.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_avamar_api.lib.worker import tasks


class TestTasks(unittest.TestCase):
    """A set of test cases for tasks.py"""
    @patch.object(tasks, 'vmware')
    def test_show_ok(self, fake_vmware):
        """``show`` returns a dictionary when everything works as expected"""
        fake_vmware.show_avamar.return_value = {'worked': True}

        output = tasks.show(username='bob', txn_id='myId')
        expected = {'content' : {'worked': True}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_show_value_error(self, fake_vmware):
        """``show`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.show_avamar.side_effect = [ValueError("testing")]

        output = tasks.show(username='bob', txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_create_ok(self, fake_vmware):
        """``create`` returns a dictionary when everything works as expected"""
        fake_vmware.create_avamar.return_value = {'worked': True}
        ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}

        output = tasks.create(username='bob',
                              machine_name='avamarBox',
                              image='0.0.1',
                              network='someLAN',
                              ip_config=ip_config,
                              txn_id='myId')
        expected = {'content' : {'worked': True}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_create_value_error(self, fake_vmware):
        """``create`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.create_avamar.side_effect = [ValueError("testing")]
        ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}

        output = tasks.create(username='bob',
                              machine_name='avamarBox',
                              image='0.0.1',
                              network='someLAN',
                              ip_config=ip_config,
                              txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_delete_ok(self, fake_vmware):
        """``delete`` returns a dictionary when everything works as expected"""
        fake_vmware.delete_avamar.return_value = {'worked': True}

        output = tasks.delete(username='bob', machine_name='avamarBox', txn_id='myId')
        expected = {'content' : {}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_delete_value_error(self, fake_vmware):
        """``delete`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.delete_avamar.side_effect = [ValueError("testing")]

        output = tasks.delete(username='bob', machine_name='avamarBox', txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_image(self, fake_vmware):
        """``image`` returns a dictionary when everything works as expected"""
        fake_vmware.list_images.return_value = ['18.2.0.134', '19.1.0.38']

        output = tasks.image(txn_id='myId')
        expected = {'content' : {'image' : ['18.2.0.134', '19.1.0.38']}, 'error': None, 'params' : {}}

        self.assertEqual(output, expected)


    @patch.object(tasks, 'vmware')
    def test_show_ndmp_ok(self, fake_vmware):
        """``show_ndmp`` returns a dictionary when everything works as expected"""
        fake_vmware.show_avamar.return_value = {'worked': True}

        output = tasks.show_ndmp(username='bob', txn_id='myId')
        expected = {'content' : {'worked': True}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_show_ndmp_value_error(self, fake_vmware):
        """``show_ndmp`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.show_avamar.side_effect = [ValueError("testing")]

        output = tasks.show_ndmp(username='bob', txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_create_ndmp_ok(self, fake_vmware):
        """``create_ndmp`` returns a dictionary when everything works as expected"""
        fake_vmware.create_avamar.return_value = {'worked': True}
        ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}

        output = tasks.create_ndmp(username='bob',
                                   machine_name='avamarBox',
                                   image='0.0.1',
                                   network='someLAN',
                                   ip_config=ip_config,
                                   txn_id='myId')
        expected = {'content' : {'worked': True}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_create_ndmp_value_error(self, fake_vmware):
        """``create_ndmp`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.create_avamar.side_effect = [ValueError("testing")]
        ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}

        output = tasks.create_ndmp(username='bob',
                                   machine_name='avamarBox',
                                   image='0.0.1',
                                   network='someLAN',
                                   ip_config=ip_config,
                                   txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_delete_ndmp_ok(self, fake_vmware):
        """``delete_ndmp`` returns a dictionary when everything works as expected"""
        fake_vmware.delete_avamar.return_value = {'worked': True}

        output = tasks.delete_ndmp(username='bob', machine_name='avamarBox', txn_id='myId')
        expected = {'content' : {}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_delete_ndmp_value_error(self, fake_vmware):
        """``delete_ndmp`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.delete_avamar.side_effect = [ValueError("testing")]

        output = tasks.delete_ndmp(username='bob', machine_name='avamarBox', txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_image_ndmp(self, fake_vmware):
        """``image_ndmp`` returns a dictionary when everything works as expected"""
        fake_vmware.list_images.return_value = ['18.2.0.134', '19.1.0.38']

        output = tasks.image_ndmp(txn_id='myId')
        expected = {'content' : {'image' : ['18.2.0.134', '19.1.0.38']}, 'error': None, 'params' : {}}

        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()
