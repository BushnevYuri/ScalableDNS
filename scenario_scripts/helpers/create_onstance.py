import os
import time
import novaclient.v3 as nvclient
from credentials import get_nova_creds

#Works!  nova boot --flavor m1.tiny --image cirros-0.3.3-x86_64 --nic net-id=ea3da9bb-b2f8-41f6-a85d-063ffbc2b2f3 --security-group default --key-name admin-key demo-instance7


image_name = "cirros-0.3.3-x86_64"
flavor = "m1.tiny"
network = "ea3da9bb-b2f8-41f6-a85d-063ffbc2b2f3"
sec_group = "default"
networks = [{"net-id": "ea3da9bb-b2f8-41f6-a85d-063ffbc2b2f3"}]

creds = get_nova_creds()
nova = nvclient.Client(**creds)

if not nova.keypairs.findall(name="demo-key"):
    with open(os.path.expanduser('/root/.ssh/id_rsa.pub')) as fpubkey:
        public_key = fpubkey.read()
        nova.keypairs.create(name="demo-key", public_key=fpubkey.read())
image = nova.images.find(name=image_name)
flavor = nova.flavors.find(name=flavor)
group = nova.security_groups.find(name=sec_group)
instance = nova.servers.create(name="test123", image=image, flavor=flavor, key_name="demo-key", nics = networks)

# Poll at 5 second intervals, until the status is no longer 'BUILD'
status = instance.status
while status == 'BUILD':
    time.sleep(5)
    # Retrieve the instance again so the status field updates
    instance = nova.servers.get(instance.id)
    status = instance.status
    print "status: %s" % status
print "End status: %s" % status