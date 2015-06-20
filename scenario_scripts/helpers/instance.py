import os
import time
import demo_user_credentials
from novaclient.v1_1 import client as nclient
from services_credentials import get_nova_creds

def create_instance(instance_name,image_name, flavor, security_group, networks):
    network = [{'net-id': networks}]

    creds = get_nova_creds()
    nova = nclient.Client(**creds)

    keypair = None
    key_name = 'demo-key9'

    openstack_keys_location = "/tmp/openstack_keys/"
    try:
        os.stat(openstack_keys_location)
    except:
        os.mkdir(openstack_keys_location)
    if not nova.keypairs.findall(name=key_name):
          os.system("nova keypair-add %s > %s/%s.pem" % (key_name, openstack_keys_location, key_name))
          os.system("chmod 600 %s/%s.pem" % (openstack_keys_location, key_name))

    image = nova.images.find(name=image_name)
    flavor = nova.flavors.find(name=flavor)
    group = nova.security_groups.find(name=security_group).name
    groups = [group]
    instance = nova.servers.create(name=instance_name, image=image, flavor=flavor, key_name=key_name, nics = network, security_groups=groups)

    #Poll at 5 second intervals, until the status is no longer 'BUILD'
    status = instance.status
    while status == 'BUILD':
          time.sleep(10)
          status = nova.servers.get(instance.id).status
          print 'Image is building...'
    print 'End status: %s' % status


    secgroup = nova.security_groups.find(name='default')

    try:
        nova.security_group_rules.create(secgroup.id,
                               ip_protocol='tcp',
                               from_port=22,
                               to_port=22)
        print 'Security tcp group rules successfully added'
    except:
        print

    try:
        nova.security_group_rules.create(secgroup.id,
                               ip_protocol='icmp',
                               from_port=-1,
                               to_port=-1)
        print 'Security icmp group rules successfully added'
    except:
        print

    nova.floating_ips.list()
    floating_ip = nova.floating_ips.create()
    instance = nova.servers.find(name=instance_name)
    instance.add_floating_ip(floating_ip)

    print "Floating ip %s added to instance" % floating_ip.ip



def remove_instance(instance_name):
    creds = get_nova_creds()
    nova = nclient.Client(**creds)
    instance = nova.servers.find(name=instance_name)
    nova.servers.delete(instance.id)
    print 'Image removed'

if __name__ == '__main__':  #TODO remove after testing
    create_instance('Ubuntu test','ubuntu_server','m1.small','default','e5a9c538-9d94-4738-ad3c-87040685692a')
    time.sleep(10)
    remove_instance('Ubuntu test')