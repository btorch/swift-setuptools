#!/bin/bash


# Info:
#       This should run on the Keystone box where you have installed the components
#       and the services are running

tenant_name="$1"
user_name="$2"
user_pass="$3"
user_role="$4"
swift_pub_domain="$5"
swift_int_domain="$6"

print "Usage: Not yet functional script"
exit 1

MY_IP=127.0.0.1
# GRIZZLY
OS_SERVICE_TOKEN=ADMIN ; OS_SERVICE_ENDPOINT=http://$MY_IP:35357/v2.0 ; export OS_SERVICE_TOKEN OS_SERVICE_ENDPOINT
# FOLSOM
# SERVICE_TOKEN=ADMIN ; SERVICE_ENDPOINT=http://$MY_IP:35357/v2.0 ; export SERVICE_TOKEN SERVICE_ENDPOINT


# Keystone User creation
tenant_id=$(keystone tenant-create --name $tenant_name --description "Tenant grouping for account users" | awk '/ id / {print $4}')
#if role ! exist; then 
#    role_id=$(keystone role-create --name $user_role | awk '/ id / {print $4}')
#done
user_id=$(keystone user-create --tenant-id $tenant_id --name $user_name --pass $user_pass  | awk '/ id / {print $4}')
keystone user-role-add --user-id $user_id --role-id $role_id --tenant-id $tenant_id


# Create a tenants:
svc_tenant_id=$(keystone tenant-create --name services --description "Tenant for account validation" | awk '/ id / {print $4}')

# Create the Services Catalog
keystone endpoint-create --region RegionOne --service-id $swift_svc_id --publicurl "http://$swift_pub_domain/v1/AUTH_\$(tenant_id)s" \
  --adminurl 'http://0.0.0.0/v1' --internalurl "http://$swift_int_domain/v1/AUTH_\$(tenant_id)s"

# - Creating the Keystone endpoint only needed with new setup
# Create the Services Catalog
# ks_svc_id=$(keystone service-create --name=keystone --type=identity --description="Keystone Identity Service"   | awk '/ id / {print $4}')
# Create Services Catalog Endpoints
# keystone endpoint-create --region RegionOne --service-id $ks_svc_id --publicurl 'http://192.168.198.10:5000/v2.0' \
#  --adminurl 'http://192.168.198.10:35357/v2.0' --internalurl 'http://192.168.198.10:5000/v2.0'
    
exit 0 
