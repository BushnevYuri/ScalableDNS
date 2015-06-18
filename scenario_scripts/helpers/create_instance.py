import os
import time
import demo_user_credentials
from novaclient.v1_1 import client as nclient
from services_credentials import get_nova_creds

def create_instance(instance_name,image_name, flavor, security_group, networks):
    network = [{'net-id': networks}]

    creds = get_nova_creds()
    nova = nclient.Client(**creds)

    if not nova.keypairs.findall(name='demo-key'):
          with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
              public_key = fpubkey.read()
              nova.keypairs.create(name='demo-key', public_key=fpubkey.read())

    image = nova.images.find(name=image_name)
    flavor = nova.flavors.find(name=flavor)
    group = nova.security_groups.find(name=security_group)

    instance = nova.servers.create(name=instance_name, image=image, flavor=flavor, key_name='demo-key', nics = network)

    #Poll at 5 second intervals, until the status is no longer 'BUILD'
    status = instance.status
    while status == 'BUILD':
          time.sleep(10)
          status = nova.servers.get(instance.id).status
          print 'Image is building...'
    print 'End status: %s' % status


    secgroup = nova.security_groups.find(name='default')
    nova.security_group_rules.create(secgroup.id,
                               ip_protocol='tcp',
                               from_port=22,
                               to_port=22)
    nova.security_group_rules.create(secgroup.id,
                               ip_protocol='icmp',
                               from_port=-1,
                               to_port=-1)


    nova.floating_ips.list()
    floating_ip = nova.floating_ips.create()
    instance = nova.servers.find(name='Ubuntu')
    instance.add_floating_ip(floating_ip)



def remove_instance(instance_name):
    creds = get_nova_creds()
    nova = nclient.Client(**creds)
    instance = nova.servers.find(name=instance_name)
    nova.servers.delete(instance.id)
    print 'Image removed'

if __name__ == '__main__':  #TODO remove after testing
    create_instance('Ubuntu test','ubuntu_server','m1.small','default','da83df25-6e68-42ca-a656-2aad2f00fcd8')
    #time.sleep(10)
    #remove_instance('Ubuntu test')