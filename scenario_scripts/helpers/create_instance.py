import os
import time
import demo_user_credentials
from novaclient.v1_1 import client as nclient
from services_credentials import get_nova_creds


#Works!  nova boot --flavor m1.tiny --image cirros-0.3.3-x86_64 --nic net-id=ea3da9bb-b2f8-41f6-a85d-063ffbc2b2f3 --security-group default --key-name admin-key demo-instance7

def create_instance(instance_name,image_name, flavor, security_group, networks):
    network = [{"net-id": networks}]

    creds = get_nova_creds()
    nova = nclient.Client(**creds)

    if not nova.keypairs.findall(name="demo-key"):
         with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
             public_key = fpubkey.read()
             nova.keypairs.create(name="demo-key", public_key=fpubkey.read())

    image = nova.images.find(name=image_name)
    flavor = nova.flavors.find(name=flavor)
    group = nova.security_groups.find(name=security_group)

    instance = nova.servers.create(name=instance_name, image=image, flavor=flavor, key_name="demo-key", nics = network)

    #Poll at 5 second intervals, until the status is no longer 'BUILD'
    status = instance.status
    while status == 'BUILD':
         time.sleep(5)
         # Retrieve the instance again so the status field updates
         instance = nova.servers.get(instance.id)
         status = instance.status
         print "status: %s" % status
    print "End status: %s" % status

if __name__ == '__main__':
    create_instance("test123","cirros-0.3.2-x86_64-uec","m1.tiny","default","69c87b69-aea2-4c09-b3f1-9de576295335")