import os

openstack_key_file = "/tmp/openstack_keys/some_key3.pem"
floating_ip = "172.24.4.11"

#os.system("scp -i " + openstack_key_file + " /home/stack/.ssh/id_rsa.pub ubuntu@" + floating_ip + ":/home/ubuntu/.ssh")

os.system("ssh-copy-id -i /home/stack/.ssh/id_rsa.pub ubuntu@" + floating_ip)

