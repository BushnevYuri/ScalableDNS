import os
import pprint
import subprocess
import time
import admin_credentials
import re
from neutronclient.neutron import client
import logging
from services_credentials import get_neutron_creds
from services_credentials import get_token

#logging.basicConfig(level=logging.INFO)
TEMP_HELPER_FILE = '/tmp/dns_scalable_helper'

neutron = client.Client('2.0',auth_url=os.environ['OS_AUTH_URL'],username='admin',password='devstack',tenant_name='demo')


def create_subnet(network_name,subnet_name,subnet_address,gateway_router_id = False, interface_router_id = False):
    network = neutron.create_network({'network':{
                                    'name': network_name,
                                    'admin_state_up': True}})
    network_id = network['network']['id']
    subnet = neutron.create_subnet({'subnet': {
                                      'name': subnet_name,
                                      'network_id': network_id,
                                      'ip_version': 4,
                                      'cidr': subnet_address}})

    if gateway_router_id:
        neutron.add_gateway_router(gateway_router_id, {'network_id':network_id} )
        print 'gateway router was added for subnet'

    if interface_router_id:
        neutron.add_interface_router(interface_router_id, {'subnet_id': subnet['subnet']['id']})
        print 'interface router was added for subnet'

    return network['network']['id']

def remove_subnet(network_name, interface_router_id = False):
     networks = neutron.list_networks(name=network_name)
     network_id = networks['networks'][0]['id']

     if interface_router_id:
        for subnet in networks['networks'][0]['subnets']:
            neutron.remove_interface_router(interface_router_id, {'subnet_id': subnet})
            print 'interface router was removed from subnet'

     neutron.delete_network(network_id)

def create_router(name, gateway_network_id = False):
    router = neutron.create_router( { 'router': { 'name': name,
                                       'admin_state_up': True} })
    if gateway_network_id :
        neutron.add_gateway_router(router['router']['id'], {'network_id':gateway_network_id} ) # external network id
    print 'Router was added'
    return router['router']['id']

def remove_router(router_id):
    neutron.delete_router(router_id)

    print 'Router was removed'

def create_load_balancer(name, load_balance_method, protocol, subnet):
    os.system('neutron lb-pool-create --lb-method %s --name %s --protocol %s --subnet-id %s --provider haproxy > %s' % (load_balance_method, name, protocol, subnet, TEMP_HELPER_FILE))
    time.sleep(5)
    load_balaner_pool_id = get_id_of_created_instance()
    os.system('neutron lb-healthmonitor-create --delay 3 --type %s --max-retries 3 --timeout 3 > %s' % (protocol, TEMP_HELPER_FILE))
    time.sleep(5)
    healthmonitor_id = get_id_of_created_instance()
    os.system('neutron lb-healthmonitor-associate %s %s' % (healthmonitor_id, name))
    print 'Load balancer created, id: %s, healthmonitor_id: %s' %(load_balaner_pool_id, healthmonitor_id)
    return load_balaner_pool_id, healthmonitor_id

def remove_load_balancer(load_balancer_pool, health_monitor=False):
    if health_monitor:
        os.system('neutron lb-healthmonitor-disassociate %s %s' % (health_monitor,load_balancer_pool))
        time.sleep(1)
        os.system('neutron lb-healthmonitor-delete %s' % health_monitor)
        time.sleep(3)
        print 'Health-monitor removed'
    os.system('neutron lb-pool-delete %s' % load_balancer_pool)
    time.sleep(3)

def add_member_to_load_balancer_pool(web_server_ip, load_balancer_pool_name, port):
    os.system('neutron lb-member-create --address  %s --protocol-port %s %s' % (web_server_ip, port, load_balancer_pool_name))
    time.sleep(3)

def create_load_balancer_virtual_ip(virtual_ip_name, port, protocol, subnet_id, load_balancer_pool_name):
    os.system('neutron lb-vip-create --name %s --protocol-port %s --protocol %s --subnet-id %s %s > %s' % (virtual_ip_name, port, protocol, subnet_id, load_balancer_pool_name, TEMP_HELPER_FILE))
    time.sleep(3)
    ip = None
    regex = re.compile("(\| address \s*\|\s)(\S*)")
    with open(TEMP_HELPER_FILE) as f:
        for line in f:
            result = regex.search(line)
            if result:
                ip = result.group(2)
    if not ip: print 'Couldn\'t get id of created instance'
    return ip

def remove_load_balancer_virtual_ip(virtual_ip_name):
    os.system('neutron lb-vip-delete --name %s' % virtual_ip_name)
    time.sleep(3)


def get_list_of_subnets():
    subnets = neutron.list_subnets()
    print subnets
    return subnets






def get_id_of_created_instance():
    id = None
    regex = re.compile("(\| id \s*\|\s)(\S*)")
    with open(TEMP_HELPER_FILE) as f:
        for line in f:
            result = regex.search(line)
            if result:
                id = result.group(2)
    if not id: print 'Couldn\'t get id of created instance'
    return id



if __name__ == '__main__':  #TODO remove after testing
    #create_external_network()
    # router_id = create_router('router1','4548790a-d4b9-4796-abd4-efda30de21a4')
    # subnet_id = create_subnet('my_network', 'my_subnet','10.0.33.0/24')
    # print "Subnet %s successfully created" % subnet_id
    # time.sleep(10)
    # remove_subnet('my_network')
    # print "Subnet %s successfully removed" % subnet_id
    # time.sleep(10)
    # remove_router(router_id)
    #remove_subnet('dns_network', interface_router_id='d5f981a1-0fa4-41cf-ac80-18f2300833b9')

    # load_balaner_pool_id, healthmonitor_id = create_load_balancer('mypool', 'SOURCE_IP', 'TCP', 'a21f4a1d-aa05-440e-ab47-5657c014d124')
    # add_member_to_load_balancer_pool ('10.0.33.1', 'mypool', 53)
    # create_load_balancer_virtual_ip('vip', 53, 'TCP', 'a21f4a1d-aa05-440e-ab47-5657c014d124', 'mypool')
    # remove_load_balancer_virtual_ip('vip')
    # remove_load_balancer('mypool', healthmonitor_id)
    get_list_of_subnets()

