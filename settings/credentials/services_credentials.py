import os
from keystoneclient.v2_0 import client

def get_nova_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']
    return d

def get_neutron_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']
    return d

def get_token():
    keystone = client.Client(username=os.environ['OS_USERNAME'],password=os.environ['OS_PASSWORD'],tenant_name=os.environ['OS_TENANT_NAME'],auth_url=os.environ['OS_AUTH_URL'])
    token_dict = keystone.auth_ref['token']['id']
    print token_dict