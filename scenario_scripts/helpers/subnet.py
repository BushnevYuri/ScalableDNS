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


def create_subnet(network_name,subnet_name,subnet_address):
    network = neutron.create_network({'network':{
                                    'name': network_name,
                                    'admin_state_up': True}})
    network_id = network['network']['id']
    subnet = neutron.create_subnet({'subnet': {
                                      'name': subnet_name,
                                      'network_id': network_id,
                                      'ip_version': 4,
                                      'cidr': subnet_address}})
    return subnet['subnet']['id']

def remove_subnet(network_name):
    networks = neutron.list_networks(name=network_name)
    network_id = networks['networks'][0]['id']
    neutron.delete_network(network_id)


if __name__ == '__main__':
    subnet_id = create_subnet('my_network', 'my_subnet','10.0.33.0/24')
    print "Subnet %s successfully created" % subnet_id
    time.sleep(10)
    remove_subnet('my_network')
    print "Subnet %s successfully removed" % subnet_id