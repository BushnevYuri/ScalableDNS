import os

os.environ["ADMIN_PASSWORD"] = "devstack"
os.environ["OS_PASSWORD"] = "devstack"
os.environ["OS_TENANT_NAME"] = "demo"
os.environ["OS_USERNAME"] = "admin"
os.environ["OS_AUTH_URL"] = "http://127.0.0.1:5000/v2.0"