#!/bin/bash

echo 'deb http://linux.dell.com/repo/community/deb/latest /' | tee -a /etc/apt/sources.list.d/linux.dell.com.sources.list
gpg --list-keys >/dev/null
gpg --keyserver pool.sks-keyservers.net --recv-key 1285491434D8786F
gpg -a --export 1285491434D8786F | apt-key add -
apt-get update -qq -o 'Acquire::http::No-Cache=True'
export DEBIAN_FRONTEND=noninteractive 
apt-get install srvadmin-all -q -y --force-yes
sleep 5
/etc/init.d/dataeng restart
