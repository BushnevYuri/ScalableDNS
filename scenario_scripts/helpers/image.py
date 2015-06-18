import admin_credentials
import keystoneclient.v2_0.client as ksclient
import glanceclient
import glanceclient.v2.client as glclient
from services_credentials import get_keystone_creds

def create_image(image_name, image_location, disk_format, container_format):
    creds = get_keystone_creds()
    keystone = ksclient.Client(**creds)
    glance_endpoint = keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
    glance = glanceclient.Client('1',glance_endpoint, token=keystone.auth_token) # first arg is version
    with open(image_location) as fimage:
        glance.images.create(name=image_name, is_public=True, disk_format=disk_format, container_format=container_format, data=fimage)

if __name__ == '__main__':  #TODO remove after testing
    create_image('ubuntu_server', '/home/stack/Downloads/precise-server-cloudimg-amd64-disk1.img', 'qcow2', 'bare')
    print "Image 'ubuntu_server' successfully created"