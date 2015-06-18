#!/usr/bin/env bash
cd /home/yurka
source admin-openrc.sh

controller_servcies=('nova-api' 'nova-cert' 'nova-consoleauth' 'nova-scheduler' 'nova-conductor')

for service in "${controller_servcies[@]}"
do
    service $service restart
done

sleep 5s
#Check statuses
printf "\n__________ Statuses __________\n"
for service in "${controller_servcies[@]}"
do
    service $service status
done
