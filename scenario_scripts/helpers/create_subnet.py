import os
import pprint
import admin_credentials
from neutronclient.neutron import client
import logging
from services_credentials import get_neutron_creds
from services_credentials import get_token

logging.basicConfig(level=logging.INFO)

######### Variables (temp) #########  TODO make as script arguments
network_name = "my_network"
subnet_name = "my_subnet"
subnet_address = '10.0.33.0/24'
####################################


neutron = client.Client('2.0',auth_url=os.environ["OS_AUTH_URL"],username='admin',password='devstack',tenant_name='demo')

network = neutron.create_network({'network':{
                                    'name': network_name,
                                    'admin_state_up': True}})

network_id = network['network']['id']

sub1 = neutron.create_subnet({'subnet': {
                                      'name': subnet_name,
                                      'network_id': network_id,
                                      'ip_version': 4,
                                      'cidr': subnet_address}})


