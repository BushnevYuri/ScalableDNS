import os
import time
import demo_user_credentials
from novaclient.v1_1 import client as nclient
from services_credentials import get_nova_creds

def create_instance(instance_name,image_name, flavor, security_group, networks, subnet_name, key_name='some_key3'):
    network = [{'net-id': networks}]

    creds = get_nova_creds()
    nova = nclient.Client(**creds)

    openstack_keys_location = "/tmp/openstack_keys/"
    openstack_key_file = openstack_keys_location + key_name + '.pem'
    try:
        os.stat(openstack_keys_location)
    except:
        os.mkdir(openstack_keys_location)
    if (not nova.keypairs.findall(name=key_name)) or (not os.stat(openstack_key_file)):
          os.system("nova keypair-add %s > %s%s.pem" % (key_name, openstack_keys_location, key_name))
          os.system("chmod 600 %s%s.pem" % (openstack_keys_location, key_name))

    temp_key = nova.keypairs.findall(name=key_name) #TODO remove(for testing)
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
    print instance.networks
    instance_ip = instance.networks[subnet_name][0]
    print "Floating ip %s added to instance" % floating_ip.ip
    return instance_ip, floating_ip, openstack_key_file



def remove_instance(instance_name):
    creds = get_nova_creds()
    nova = nclient.Client(**creds)
    instance = nova.servers.find(name=instance_name)
    nova.servers.delete(instance.id)
    print 'Image removed'

if __name__ == '__main__':  #TODO remove after testing
    create_instance('test','ubuntu_server','m1.small','default','9b0bbc98-fd65-4f77-acd4-e1380b49267b','test')
    #time.sleep(10)
    #remove_instance('Ubuntu test')