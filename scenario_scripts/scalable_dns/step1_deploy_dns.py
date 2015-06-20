import time
from instance import *
from subnet import *

########  Variables  #########

NETWORK_NAME = 'dns_network'
SUBNET_NAME = 'dns_network'
SUBNET_ADDRESS = '10.0.33.0/24'
EXTERNAL_NETWORK_ID = '4548790a-d4b9-4796-abd4-efda30de21a4'

DNS_SERVERS = [] # DNS instances names
DNS_SERVER_IMAGE = 'cirros-0.3.2-x86_64-uec' #'ubuntu_server'
DNS_SERVERS_FLAVOR = 'm1.small'
DNS_SECURITY_GROUP = 'default'
BASE_ROUTER = 'router'
##############################

def purge_dns(router_id):
    for instance in DNS_SERVERS:
        remove_instance(instance)
    print "wait a while for nova to release ports"
    time.sleep(5)

    remove_subnet(NETWORK_NAME, router_id)
    remove_router(router_id)

if __name__ == '__main__':  #TODO remove after testing
    router_id = create_router(BASE_ROUTER, EXTERNAL_NETWORK_ID)
    subnet_id = create_subnet(NETWORK_NAME, SUBNET_NAME, SUBNET_ADDRESS, interface_router_id=router_id)
    instance_name = 'dns_%s' % time.time()
    create_instance(instance_name, DNS_SERVER_IMAGE, DNS_SERVERS_FLAVOR, DNS_SECURITY_GROUP, subnet_id)
    DNS_SERVERS.append(instance_name)

    #TODO deploy dns on created node or create predifined image with dns server

    purge_dns(router_id)










