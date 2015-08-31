import paramiko
from instance import *
from subnet import *

########  Variables  #########

#Need to change value after each stack rerun ('how to' check in video)
EXTERNAL_NETWORK_ID = '62222b3b-51f2-432c-9248-f82fe717c099'


NETWORK_NAME = 'dns_network'
SUBNET_NAME = 'dns_network'
SUBNET_ADDRESS = '10.0.33.0/24'


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
    """
    If something goes wrong, this function will clean whole environment after failure
    :return:
    """
    remove_load_balancer_virtual_ip(LOAD_BALANCER_VIP)
    remove_load_balancer(LOAD_BALANCER_POOL_NAME, healthmonitor_id)
    for instance in instances_list:
        remove_instance(instance)
    print "wait a while for nova to release ports"
    time.sleep(5)

    remove_subnet(NETWORK_NAME, router_id)
    remove_router(router_id)

def get_number_of_subnets_for_dns_vip(dns_vip_ip):
    """
    :return: Number of subnets which is managed by one dns with specified ip
    """
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

def add_additional_dns_node(subnet_id, image_name, sync_up = False):
    instance_name = 'dns_%s' % time.time()
    instance_ip, floating_ip, openstack_key_file = create_instance(instance_name, image_name, DNS_SERVERS_FLAVOR, DNS_SECURITY_GROUP, subnet_id, SUBNET_NAME)
    DNS_SERVERS.append(instance_name)
    add_member_to_load_balancer_pool (instance_ip, LOAD_BALANCER_POOL_NAME, LOAD_BALANCER_PORT) #add created instance to load balancer pool

    key = paramiko.RSAKey.from_private_key_file(openstack_key_file)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # to avoid any user interactions while ssh login

    print "Instance %s was successfully added" % instance_name
    for x in range(20):
        try:
            ssh.connect(floating_ip.ip, username=CLOUD_IMAGE_USERNAME, pkey=key, timeout=300)
            print 'connected'
            #TODO Need to add script for simple web service which will have some state
            #ssh.exec_command('touch %s' % instance_name)
            #ssh.exec_command('sudo python -m SimpleHTTPServer 80 > /dev/null 2>&1 &')

            ssh.close()
            return (floating_ip, key)
        except Exception:
            print 'Ssh connecting...'
            time.sleep(15)
    print 'Unable to ssh to created instance'



if __name__ == '__main__':
    try:
        print 'Starting dns...'
        router_id = create_router(BASE_ROUTER, EXTERNAL_NETWORK_ID)
        'Dns router was added, id: %s' % router_id
        subnet_id = create_subnet(NETWORK_NAME, SUBNET_NAME, SUBNET_ADDRESS, interface_router_id=router_id)
        load_balaner_pool_id, healthmonitor_id = create_load_balancer(LOAD_BALANCER_POOL_NAME, LOAD_BALANCER_METHOD, LOAD_BALANCER_PROTOCOL, SUBNET_NAME)
        ip = create_load_balancer_virtual_ip(LOAD_BALANCER_VIP, LOAD_BALANCER_PORT, LOAD_BALANCER_PROTOCOL, SUBNET_NAME, LOAD_BALANCER_POOL_NAME) # to have one entry point for all NFV members
        print 'VIP for load dns load balancer: %s' % ip
        ret_val  = add_additional_dns_node(subnet_id, "NFV_instance1")
        floating_ip = ret_val[0]
        key  = ret_val[1]

        # #TODO deploy dns on created node or create predifined image with dns server
        sync = None
        sync_up_ip = None
        while (True):
             time.sleep(20)  #should be ~several secs in production. Each iteration we check if there is a need to create new NFV instance and also perform state sync up in existing

             if (sync):
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(floating_ip.ip, username=CLOUD_IMAGE_USERNAME, pkey=key, timeout=300)

                #FIRST BREAKPOINT
                ssh.exec_command('sudo unison -auto -batch /tmp ssh://'+ sync_up_ip.ip +'//tmp')
                ssh.close()

             #SECOND BREAKPOINT
             subnets_count = get_number_of_subnets_for_dns_vip(ip)
             if DNS_SERVERS.__len__() * SUBNETS_PER_SERVICE_NODE <= subnets_count:
                 ret_val = add_additional_dns_node(subnet_id, "NFV_instance2")
                 sync_up_ip = ret_val[0]
                 sync = True

    finally:
        print "Teardown" # if something goes wrong this step just clean all environment to avoid manual clean up each time
        purge_dns(router_id, healthmonitor_id)








