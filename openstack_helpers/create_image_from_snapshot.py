import os
import admin_credentials

os.system("glance --os-image-api-version 2 image-list")

os.system("glance image-download  6317a684-dfa3-493f-a407-7fdf2950a846 --file /home/stack/NFV_instance2.img")

