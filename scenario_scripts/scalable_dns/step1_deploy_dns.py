import time
from instance import *
from subnet import *

########  Variables  #########

NETWORK_NAME = 'dns_network'
SUBNET_NAME = 'dns_network'
SUBNET_ADDRESS = '10.0.33.0/24'
EXTERNAL_NETWORK_ID = 'cf59e13f-b730-49a5-ba12-6d77ae02a1c7'

DNS_SERVERS = [] # DNS instances names
DNS_SERVER_IMAGE = 'ubuntu_server' #'cirros-0.3.2-x86_64-uec'
DNS_SERVERS_FLAVOR = 'm1.small'
DNS_SECURITY_GROUP = 'default'
BASE_ROUTER = 'router'

LOAD_BALANCER_POOL_NAME = 'dns_load_balancer'
LOAD_BALANCER_METHOD = 'SOURCE_IP'
LOAD_BALANCER_PROTOCOL = 'TCP'
LOAD_BALANCER_PORT = 53
LOAD_BALANCER_VIP = 'dns_vip'

SUBNETS_PER_SERVICE_NODE = 1
##############################

def purge_dns(router_id, healthmonitor_id):
    remove_load_balancer_virtual_ip(LOAD_BALANCER_VIP)
    remove_load_balancer(LOAD_BALANCER_POOL_NAME, healthmonitor_id)
    for instance in DNS_SERVERS:
        remove_instance(instance)
    print "wait a while for nova to release ports"
    time.sleep(5)

    remove_subnet(NETWORK_NAME, router_id)
    remove_router(router_id)

def get_number_of_subnets_for_dns_vip(dns_vip_ip):
    subnets_count = 0
    subnets = get_list_of_subnets()
    for subnet in subnets['subnets']:
        dns_servers = subnet['dns_nameservers']
        if dns_servers:
            for server in dns_servers:
                if server == dns_vip_ip:
                    subnets_count += 1
    print 'Subnets count for dns pool is %s' % subnets_count
    return subnets_count

def add_additional_dns_node(subnet_id):
    instance_name = 'dns_%s' % time.time()
    instance_ip = create_instance(instance_name, DNS_SERVER_IMAGE, DNS_SERVERS_FLAVOR, DNS_SECURITY_GROUP, subnet_id)
    DNS_SERVERS.append(instance_name)
    add_member_to_load_balancer_pool (instance_ip, LOAD_BALANCER_POOL_NAME, LOAD_BALANCER_PORT)







if __name__ == '__main__':  #TODO remove after testing
   # purge_dns('36d317ae-ef93-4c45-943b-711bb64d3d54', 'b502cc95-437b-4430-97b6-03bb5f147bd7')
  #  time.sleep(300)
    try:
        router_id = create_router(BASE_ROUTER, EXTERNAL_NETWORK_ID)
        subnet_id = create_subnet(NETWORK_NAME, SUBNET_NAME, SUBNET_ADDRESS, interface_router_id=router_id)
        instance_name = 'dns_%s' % time.time()
        instance_ip = create_instance(instance_name, DNS_SERVER_IMAGE, DNS_SERVERS_FLAVOR, DNS_SECURITY_GROUP, subnet_id)
        DNS_SERVERS.append(instance_name)
        load_balaner_pool_id, healthmonitor_id = create_load_balancer(LOAD_BALANCER_POOL_NAME, LOAD_BALANCER_METHOD, LOAD_BALANCER_PROTOCOL, SUBNET_NAME)
        add_member_to_load_balancer_pool (instance_ip, LOAD_BALANCER_POOL_NAME, LOAD_BALANCER_PORT)
        create_load_balancer_virtual_ip(LOAD_BALANCER_VIP, LOAD_BALANCER_PORT, LOAD_BALANCER_PROTOCOL, SUBNET_NAME, LOAD_BALANCER_POOL_NAME)

        #TODO deploy dns on created node or create predifined image with dns server
        # while (True):
        #     time.sleep(5)
        #     subnets_count = get_number_of_subnets_for_dns_vip('8.8.8.8')
        #     if DNS_SERVERS.__len__() * SUBNETS_PER_SERVICE_NODE <= subnets_count:
        #         add_additional_dns_node(subnet_id)
    finally:
        print "Teardown"
        #purge_dns(router_id, healthmonitor_id)








