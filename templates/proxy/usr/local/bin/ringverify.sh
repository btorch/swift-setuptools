#!/bin/bash

# Info:
#   This script just grabs the ring.md5sum file from the ringserver
#   and validates the local ring files

RINGSERVERIP="$1"

if [ -z "$RINGSERVERIP" ]; then
    echo "Need Ring Server IP as valid argument"
    exit 1
fi


LOCKFILE=/var/lock/.ringcheck.lock
if [ -e $LOCKFILE ]; then
    exit 1
else
    #create lock file
    touch $LOCKFILE
fi

cd /etc/swift
w3m -dump http://$RINGSERVERIP/ring/ring.md5sum | md5sum -c --quiet

rm -f $LOCKFILE
exit 0

