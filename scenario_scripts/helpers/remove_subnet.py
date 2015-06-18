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
####################################


neutron = client.Client('2.0',auth_url=os.environ["OS_AUTH_URL"],username='admin',password='devstack',tenant_name='demo')

networks = neutron.list_networks(name=network_name)
network_id = networks['networks'][0]['id']
neutron.delete_network(network_id)