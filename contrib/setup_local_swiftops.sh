#!/bin/bash

# Info:
#       Creates local swiftops user
#       Sets ssh rsa key
#       Setups up sudoers file
#

/bin/sed -i 's/^%sudo.*/%sudo ALL=NOPASSWD: ALL/'  /etc/sudoers 
/bin/chmod 0440 /etc/sudoers
/usr/sbin/useradd -G sudo -s /bin/bash -c "Openstack Swift OP User" -m swiftops
sudo -u swiftops sh -c '/usr/bin/ssh-keygen -t rsa -N "" -f /home/swiftops/.ssh/id_rsa'
sudo -u swiftops sh -c 'printf "StrictHostKeyChecking no\nUserKnownHostsFile /dev/null\nLogLevel quiet\n" > /home/swiftops/.ssh/config'
