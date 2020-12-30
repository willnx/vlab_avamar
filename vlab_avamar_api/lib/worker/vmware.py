# -*- coding: UTF-8 -*-
"""Business logic for backend worker tasks"""
import time
import os.path
from vlab_inf_common.vmware import vCenter, Ova, vim, virtual_machine, consume_task

from vlab_avamar_api.lib import const


def show_avamar(username):
    """Obtain basic information about Avamar

    :Returns: Dictionary

    :param username: The user requesting info about their Avamar
    :type username: String
    """
    info = {}
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        avamar_vms = {}
        for vm in folder.childEntity:
            info = virtual_machine.get_info(vcenter, vm, username)
            if info['meta']['component'] == 'Avamar':
                avamar_vms[vm.name] = info
    return avamar_vms


def delete_avamar(username, machine_name, logger):
    """Unregister and destroy a user's Avamar

    :Returns: None

    :param username: The user who wants to delete their jumpbox
    :type username: String

    :param machine_name: The name of the VM to delete
    :type machine_name: String

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for entity in folder.childEntity:
            if entity.name == machine_name:
                info = virtual_machine.get_info(vcenter, entity, username)
                if info['meta']['component'] == 'Avamar':
                    logger.debug('powering off VM')
                    virtual_machine.power(entity, state='off')
                    delete_task = entity.Destroy_Task()
                    logger.debug('blocking while VM is being destroyed')
                    consume_task(delete_task)
                    break
        else:
            raise ValueError('No {} named {} found'.format('avamar', machine_name))


def create_avamar(username, machine_name, image, network, ip_config, logger):
    """Deploy a new instance of Avamar

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new Avamar
    :type username: String

    :param machine_name: The name of the new instance of Avamar
    :type machine_name: String

    :param image: The image/version of Avamar to create
    :type image: String

    :param network: The name of the network to connect the new Avamar instance up to
    :type network: String

    :param ip_config: The IPv4 network configuration for the Avamar instance.
    :type ip_config: Dictionary

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER,
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        image_name = convert_name(image)
        logger.info('Deploying image %s', image_name)
        ova = Ova(os.path.join(const.VLAB_AVAMAR_IMAGES_DIR, image_name))
        try:
            network_map = vim.OvfManager.NetworkMapping()
            network_map.name = ova.networks[0]
            try:
                network_map.network = vcenter.networks[network]
            except KeyError:
                raise ValueError('No such network named {}'.format(network))
            the_vm = virtual_machine.deploy_from_ova(vcenter=vcenter,
                                                     ova=ova,
                                                     network_map=[network_map],
                                                     username=username,
                                                     machine_name=machine_name,
                                                     logger=logger)
        finally:
            ova.close()
        logger.info('Blocking while VM boots')
        # For whatever reason, we have to power on the machine before vSphere
        # will recognize that VMware Tools is installed. From that point, we
        # can then power off the machine to configure the network. Fun, right?
        _block_on_boot(the_vm)
        logger.info("Powering Off VM")
        virtual_machine.power(the_vm, state='off')
        logger.info("Configuring Network")
        _configure_network(the_vm, ip_config)
        logger.info("Powering on VM")
        virtual_machine.power(the_vm, state='on')
        meta_data = {'component' : "Avamar",
                     'created' : time.time(),
                     'version' : image,
                     'configured' : True,
                     'generation' : 1}
        virtual_machine.set_meta(the_vm, meta_data)
        info = virtual_machine.get_info(vcenter, the_vm, username, ensure_ip=True)
        return  {the_vm.name: info}


def list_images():
    """Obtain a list of available versions of Avamar that can be created

    :Returns: List
    """
    images = os.listdir(const.VLAB_AVAMAR_IMAGES_DIR)
    images = [convert_name(x, to_version=True) for x in images]
    return images


def convert_name(name, to_version=False):
    """This function centralizes converting between the name of the OVA, and the
    version of software it contains.

    :param name: The thing to covert
    :type name: String

    :param to_version: Set to True to covert the name of an OVA to the version
    :type to_version: Boolean
    """
    if to_version:
        return name.split('-')[-1].replace('.ova', '')
    else:
        return 'AVE-{}.ova'.format(name)


def _configure_network(the_vm, ip_config):
    # Boilerplate...
    adaptermap = vim.vm.customization.AdapterMapping()
    globalip = vim.vm.customization.GlobalIPSettings()
    adaptermap.adapter = vim.vm.customization.IPSettings()
    # Configure IP & DNS
    adaptermap.adapter.ip = vim.vm.customization.FixedIp()
    adaptermap.adapter.ip.ipAddress = ip_config['static-ip']
    adaptermap.adapter.subnetMask = ip_config['netmask']
    adaptermap.adapter.gateway = ip_config['default-gateway']
    globalip.dnsServerList = ip_config['dns']
    adaptermap.adapter.dnsDomain = ip_config['domain']
    ident = vim.vm.customization.LinuxPrep()
    ident.domain = ip_config['domain']
    ident.hostName = vim.vm.customization.FixedName()
    ident.hostName.name = the_vm.name
    # Create the configuration spec
    spec = vim.vm.customization.Specification()
    spec.nicSettingMap = [adaptermap]
    spec.globalIPSettings = globalip
    spec.identity = ident
    task = the_vm.Customize(spec=spec)
    consume_task(task)


def _block_on_boot(the_vm):
    ready = the_vm.guest.toolsStatus == vim.vm.GuestInfo.ToolsStatus.toolsOk
    while not ready:
        time.sleep(1)
        ready = the_vm.guest.toolsStatus == vim.vm.GuestInfo.ToolsStatus.toolsOk
    # Fun fact - it's still booting. If we don't let it fully boot, then the
    # for whatever reason the network changes will be tossed out. Thanks Avamar!
    # So, let's just do a dumb long sleep and hope :(
    time.sleep(300)
