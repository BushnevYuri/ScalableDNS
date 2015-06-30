import time
import paramiko
from instance import *
from subnet import *

########  Variables  #########

NETWORK_NAME = 'dns_network'
SUBNET_NAME = 'dns_network'
SUBNET_ADDRESS = '10.0.33.0/24'
EXTERNAL_NETWORK_ID = '68b807d5-3ce5-497f-8bf1-984c3eebcbde'

DNS_SERVERS = [] # DNS instances names
DNS_SERVER_IMAGE = 'ubuntu_server' #'cirros-0.3.2-x86_64-uec'
CLOUD_IMAGE_USERNAME = 'ubuntu'
DNS_SERVERS_FLAVOR = 'm1.small'
DNS_SECURITY_GROUP = 'default'
BASE_ROUTER = 'router'

LOAD_BALANCER_POOL_NAME = 'dns_load_balancer'
LOAD_BALANCER_METHOD = 'SOURCE_IP'
LOAD_BALANCER_PROTOCOL = 'HTTP'
LOAD_BALANCER_PORT = 80
LOAD_BALANCER_VIP = 'dns_vip'

SUBNETS_PER_SERVICE_NODE = 1
##############################

def purge_dns(router_id, healthmonitor_id, instances_list=DNS_SERVERS):
    remove_load_balancer_virtual_ip(LOAD_BALANCER_VIP)
    remove_load_balancer(LOAD_BALANCER_POOL_NAME, healthmonitor_id)
    for instance in instances_list:
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
    instance_ip, floating_ip, openstack_key_file = create_instance(instance_name, DNS_SERVER_IMAGE, DNS_SERVERS_FLAVOR, DNS_SECURITY_GROUP, subnet_id, SUBNET_NAME)
    DNS_SERVERS.append(instance_name)
    add_member_to_load_balancer_pool (instance_ip, LOAD_BALANCER_POOL_NAME, LOAD_BALANCER_PORT)

    key = paramiko.RSAKey.from_private_key_file(openstack_key_file)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print "Instance %s was successfully added" % instance_name
    for x in range(20):
        try:
            ssh.connect(floating_ip.ip, username=CLOUD_IMAGE_USERNAME, pkey=key, timeout=300)
            print 'connected'
            ssh.exec_command('touch %s' % instance_name)
            ssh.exec_command('sudo python -m SimpleHTTPServer 80 > /dev/null 2>&1 &')
            ssh.close()
            return True
        except Exception:
            print 'Ssh connecting...'
            time.sleep(15)
    print 'Unable to ssh to created instance'



if __name__ == '__main__':  #TODO remove after testing
    #purge_dns('58d52cb9-72be-40ff-a8ca-5f104d0bc9eb', 'ee50e206-d1f4-447c-bf74-8449f02933ad',['c41b6b11-d439-4e40-8100-f80954f73667','0ebb7743-6f32-4bf4-a1b3-1eace3e1eae5','4e5deee4-674c-4696-bd30-9b8a82dcc8c8','aa12cdf4-d504-4a24-abef-5d684cf4f99b'])
    try:
        print 'Starting dns...'
        router_id = create_router(BASE_ROUTER, EXTERNAL_NETWORK_ID)
        'Dns router was added, id: %s' % router_id
        subnet_id = create_subnet(NETWORK_NAME, SUBNET_NAME, SUBNET_ADDRESS, interface_router_id=router_id)
        load_balaner_pool_id, healthmonitor_id = create_load_balancer(LOAD_BALANCER_POOL_NAME, LOAD_BALANCER_METHOD, LOAD_BALANCER_PROTOCOL, SUBNET_NAME)
        ip = create_load_balancer_virtual_ip(LOAD_BALANCER_VIP, LOAD_BALANCER_PORT, LOAD_BALANCER_PROTOCOL, SUBNET_NAME, LOAD_BALANCER_POOL_NAME)
        print 'VIP for load dns load balancer: %s' % ip
        add_additional_dns_node(subnet_id)

        #TODO deploy dns on created node or create predifined image with dns server
        while (True):
             time.sleep(5)
             subnets_count = get_number_of_subnets_for_dns_vip(ip)
             if DNS_SERVERS.__len__() * SUBNETS_PER_SERVICE_NODE <= subnets_count:
                 add_additional_dns_node(subnet_id)
    finally:
        print "Teardown"
        purge_dns(router_id, healthmonitor_id)








