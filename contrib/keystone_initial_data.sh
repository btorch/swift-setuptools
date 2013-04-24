#!/bin/bash


# Info:
#       This should run on the Keystone box where you have installed the components
#       and the services are running

PUB_DOMAIN="pub-swift.domain.com"
INT_DOMAIN="int-swift.domain.com"

MY_IP=127.0.0.1
# GRIZZLY
OS_SERVICE_TOKEN=ADMIN
OS_SERVICE_ENDPOINT=http://$MY_IP:35357/v2.0
export OS_SERVICE_TOKEN OS_SERVICE_ENDPOINT
# FOLSOM
#SERVICE_TOKEN=ADMIN
#SERVICE_ENDPOINT=http://$MY_IP:35357/v2.0
#export SERVICE_TOKEN SERVICE_ENDPOINT

# Create a tenants:
tenant_id=$(keystone tenant-create --name users --description "Tenant grouping for general users" | awk '/ id / {print $4}')
svc_tenant_id=$(keystone tenant-create --name services --description "Tenant grouping for available services" | awk '/ id / {print $4}')

# Create regular users & admin roles:
admin_role_id=$(keystone role-create --name admin | awk '/ id / {print $4}')
role_id=$(keystone role-create --name general  | awk '/ id / {print $4}')

# Create the new users:
user_id=$(keystone user-create --tenant-id $tenant_id --name swiftops --pass swift2014  | awk '/ id / {print $4}')
admin_user_id=$(keystone user-create --tenant-id $tenant_id --name oskadmin --pass osk2014   | awk '/ id / {print $4}')

# Grant Roles to users
keystone user-role-add --user-id $user_id --role-id $role_id --tenant-id $tenant_id
keystone user-role-add --user-id $admin_user_id --role-id $admin_role_id --tenant-id $tenant_id 

# Create the Services Catalog
ks_svc_id=$(keystone service-create --name=keystone --type=identity --description="Keystone Identity Service"   | awk '/ id / {print $4}')
swift_svc_id=$(keystone service-create --name=swift --type=object-store --description="Swift Service"  | awk '/ id / {print $4}')

# Create Services Catalog Endpoints
keystone endpoint-create --region RegionOne --service-id $ks_svc_id --publicurl 'http://166.78.157.81:5000/v2.0' \
  --adminurl 'http://172.16.0.2:35357/v2.0' --internalurl 'http://172.16.0.2:5000/v2.0'
keystone endpoint-create --region RegionOne --service-id $swift_svc_id --publicurl "http://$PUB_DOMAIN/v1/AUTH_\$(tenant_id)s" \
  --adminurl 'http://0.0.0.0/v1' --internalurl "http://$INT_DOMAIN/v1/AUTH_\$(tenant_id)s"
    
exit 0 
