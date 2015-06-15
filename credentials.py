import os

os.environ["OS_TENANT_NAME"] = "admin"
os.environ["OS_USERNAME"] = "admin"
os.environ["OS_PASSWORD"] = "openstack"
os.environ["OS_AUTH_URL"] = "http://controller:35357/v2.0"

def get_nova_creds():
    credentials = {}
    credentials['username'] = os.environ['OS_USERNAME']
    credentials['api_key'] = os.environ['OS_PASSWORD']
    credentials['auth_url'] = os.environ['OS_AUTH_URL']
    credentials['project_id'] = os.environ['OS_TENANT_NAME']
    return credentials