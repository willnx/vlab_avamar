# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock, PropertyMock

from vlab_avamar_api.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for the vmware.py module"""

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_show_avamar(self, fake_vCenter, fake_consume_task, fake_get_info):
        """``avamar`` returns a dictionary when everything works as expected"""
        fake_vm = MagicMock()
        fake_vm.name = 'Avamar'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta': {'component': 'Avamar',
                                               'created': 1234,
                                               'version': '1.0',
                                               'configured': False,
                                               'generation': 1}}

        output = vmware.show_avamar(username='alice')
        expected = {'Avamar': {'meta': {'component': 'Avamar',
                                                             'created': 1234,
                                                             'version': '1.0',
                                                             'configured': False,
                                                             'generation': 1}}}
        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_avamar(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_avamar`` returns None when everything works as expected"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'AvamarBox'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta': {'component': 'Avamar',
                                               'created': 1234,
                                               'version': '1.0',
                                               'configured': False,
                                               'generation': 1}}

        output = vmware.delete_avamar(username='bob', machine_name='AvamarBox', logger=fake_logger)
        expected = None

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_avamar_value_error(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_avamar`` raises ValueError when unable to find requested vm for deletion"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'win10'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta': {'component': 'Avamar',
                                               'created': 1234,
                                               'version': '1.0',
                                               'configured': False,
                                               'generation': 1}}

        with self.assertRaises(ValueError):
            vmware.delete_avamar(username='bob', machine_name='myOtherAvamarBox', logger=fake_logger)

    @patch.object(vmware, '_block_on_boot')
    @patch.object(vmware, '_configure_network')
    @patch.object(vmware.virtual_machine, 'set_meta')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_avamar(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info,
                           fake_Ova, fake_set_meta, fake__configure_network, fake_block_on_boot):
        """``create_avamar`` returns a dictionary upon success"""
        fake_logger = MagicMock()
        fake_deploy_from_ova.return_value.name = 'myAvamar'
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}
        ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}


        output = vmware.create_avamar(username='alice',
                                       machine_name='AvamarBox',
                                       image='1.0.0',
                                       network='someLAN',
                                       ip_config=ip_config,
                                       logger=fake_logger)
        expected = {'myAvamar': {'worked': True}}

        self.assertEqual(output, expected)

    @patch.object(vmware, '_configure_network')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_avamar_invalid_network(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_configure_network):
        """``create_avamar`` raises ValueError if supplied with a non-existing network"""
        fake_logger = MagicMock()
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}
        ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}

        with self.assertRaises(ValueError):
            vmware.create_avamar(username='alice',
                                  machine_name='AvamarBox',
                                  image='1.0.0',
                                  network='someOtherLAN',
                                  ip_config=ip_config,
                                  logger=fake_logger)

    @patch.object(vmware.os, 'listdir')
    def test_list_images(self, fake_listdir):
        """``list_images`` - Returns a list of available Avamar versions that can be deployed"""
        fake_listdir.return_value = ['AVE-18.2.0.134.ova',  'AVE-19.1.0.38.ova',  'AVE-19.2.0.155b.ova']

        output = vmware.list_images()
        expected = ['18.2.0.134', '19.1.0.38', '19.2.0.155b']

        # set() avoids ordering issue in test
        self.assertEqual(set(output), set(expected))

    def test_convert_name(self):
        """``convert_name`` - defaults to converting to the OVA file name"""
        output = vmware.convert_name(name='1.0.0', kind='Avamar')
        expected = 'AVE-1.0.0.ova'

        self.assertEqual(output, expected)

    def test_convert_name_to_version(self):
        """``convert_name`` - can take a OVA file name, and extract the version from it"""
        output = vmware.convert_name('AVE-19.1.0.38.ova', kind='Avamar', to_version=True)
        expected = '19.1.0.38'

        self.assertEqual(output, expected)

    def test_convert_name_ndmp(self):
        """``convert_name`` - defaults to converting to the OVA file name"""
        output = vmware.convert_name(name='1.0.0', kind='AvamarNDMP')
        expected = 'NDMP-1.0.0.ova'

        self.assertEqual(output, expected)

    def test_convert_name_to_version_ndmp(self):
        """``convert_name`` - can take a OVA file name, and extract the version from it"""
        output = vmware.convert_name('AVE-19.1.0.38.ova', kind='AvamarNDMP', to_version=True)
        expected = '19.1.0.38'

        self.assertEqual(output, expected)

    @patch.object(vmware, 'consume_task')
    def test_configure_network(self, fake_consume_task):
        """``_configure_network`` - Blocks while configuring the VM"""
        the_vm = MagicMock()
        the_vm.name = 'myAvamarInstance'
        ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}

        vmware._configure_network(the_vm, ip_config)

        self.assertTrue(fake_consume_task.called)

    @patch.object(vmware.time, 'sleep')
    def test_block_on_boot(self, fake_sleep):
        """``_block_on_boot`` waits for VMware Tools to be ready"""
        the_vm = MagicMock()
        toolsStatus = PropertyMock(side_effect=['notready', vmware.vim.vm.GuestInfo.ToolsStatus.toolsOk])
        type(the_vm.guest).toolsStatus = toolsStatus

        vmware._block_on_boot(the_vm)

        # 2 calls to sleep - 1 when VMware Tools is not ready, then a second
        # to continue blocking in hopes that the VM completes booting.
        self.assertEqual(2, fake_sleep.call_count)



if __name__ == '__main__':
    unittest.main()
