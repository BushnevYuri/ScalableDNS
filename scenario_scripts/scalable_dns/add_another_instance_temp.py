import time
import paramiko
from instance import *
from subnet import *

EXTERNAL_NETWORK_ID = 'ae91aac1-2bc9-4dd3-9ef7-f6bf6d1e8ea6'

########  Variables  #########

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
            #ssh.exec_command('touch %s' % instance_name)
            #ssh.exec_command('sudo python -m SimpleHTTPServer 80 > /dev/null 2>&1 &')

            # print 'Unison installation step 1'
            # stdin, stdout, stderr = ssh.exec_command('sudo add-apt-repository ppa:pascal-bach/unison')
            # print 'Unison installation step 2'
            # stdin, stdout, stderr = ssh.exec_command('sudo apt-get update')
            # channel = stdout.channel
            # status = channel.recv_exit_status()
            # print "Before installation"
            # stdin, stdout, stderr = ssh.exec_command('sudo apt-get install unison')
            # channel = stdout.channel
            # status = channel.recv_exit_status()
            # print 'After installation'
            #
            # os.system("scp -i " + openstack_key_file + " /home/stack/.ssh/id_rsa.pub ubuntu@" + floating_ip + ":/home/ubuntu/.ssh")


            ssh.close()
            return True
        except Exception:
            print 'Instance is booting... \n *Use real OpenStack instead of DevStack if you don\'t wnat to wait so long =)\n'
            time.sleep(20)
    print 'Unable to ssh to created instance'


if __name__ == '__main__':  #TODO remove after testing
     add_additional_dns_node('265757a3-9565-4e1e-bcbf-b2ba38884f0b')