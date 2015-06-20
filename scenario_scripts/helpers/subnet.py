import os
import pprint
import time
import admin_credentials
from neutronclient.neutron import client
import logging
from services_credentials import get_neutron_creds
from services_credentials import get_token

#logging.basicConfig(level=logging.INFO)

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

    remove_subnet('dns_network', interface_router_id='d5f981a1-0fa4-41cf-ac80-18f2300833b9')
