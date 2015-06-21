# ScalableDNS
Initial POC of framework for writing basic scenarios on openstack for NFV research work.

Contains functions which are more highlevel abstracted and don't need additional steps for authentication and so on..
Instead of triggering lots of API calls, it will be enough just to run one script which will create:
-external subnet
-router with interfaces
-internal subnet
-instances
-and so on..

In the same time, this script could ve used further as one building block for another scenarios.

