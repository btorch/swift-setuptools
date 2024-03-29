#!/bin/bash

# Author: Marcelo Martins
# Date: 2013-04-02
# Version: 1.00
#
# Info:
#   Quick script for setting up the drives for swift storage nodes
#
# Attention:
#   On a real system, I usually have a udev file created for the drives
#   in order to maintain a sane device block order otherwise somtimes the kernel
#   may choose another label for a drive that has been hot swapped. 
#   The udev rules are created mapping each device block ID to a SYMLINK of
#   format cXuYp, where X is the controller number and Y the unit number.
#
#   On a VM system, it's a whole other story and therefore a drive_list
#   would be used to figure those out.
#



# ARGUMENTS
num_of_args=$#
args_sarray=("$@")

# Variables
parted=/sbin/parted
mkfs=/sbin/mkfs.xfs
sed=/bin/sed
inode_size=512


usage_display (){
cat << USAGE

Syntax:
    sudo setup_drives.sh [-l "drive_list"] [-o] | [ [-c number | -p mapper_prefix] -s num -e num] [-o]
        -p  Device prefix for mapper setups. e.g: mpath, lvm ... etc (Use double quotes)
        -l  List of devices to be setup e.g: "xvdb xvdd xvdf xvdg" (Use double quotes)
        -c  Controller nummber in case you are using the cXuYp udev formatting 
        -s  The first unit to start the drive setup from
        -e  The last unit that the drive setup will run on
        -o  Allows the override and will partition and format c0u0p (Becareful: ususally OS drive)
        -h For this usage screen

    NOTE: The -c/-s/-e options cannot be used when -V is declared
          If a partition already exist for a device it will be DESTROYED

USAGE
exit 1
}


# Parsing arguments
while getopts "ol:c:s:e:p:h" opts
do
    case $opts in         
        p)
            device_prefix="${OPTARG}"
        ;;
        o)
            override=1
        ;;
        l)
            drive_list="${OPTARG}"
        ;;
        c)
            controller_num="${OPTARG}"
            if [[ $controller_num -gt 5 ]]; then
                printf "\n\t Error: controller nummber too high (max=5)\n"
                usage_display
            fi
        ;;
        s)
            unit_start="${OPTARG}"
        ;;
        e)
            unit_end="${OPTARG}"
        ;;
        *)
            usage_display
        ;;
    esac           
done


# Check on ARGS count
if [[ $num_of_args -lt 2 ]]; then 
    printf "\n\t Error: Must have at least 2 arguments given\n"
    usage_display
fi

# Checking ARGS passed
if [[ ! -z "$controller_num" ]] && [[ ! -z $device_prefix ]]; then 
    printf "\n\t Error: cannot use both -c and -p\n"
    usage_display
fi
if [[ ! -z "$controller_num" ]] && [[ ! -z $drive_list ]]; then 
    printf "\n\t Error: cannot use both -c and -l\n"
    usage_display
fi
if [[ ! -z "$device_prefix" ]] && [[ ! -z $drive_list ]]; then 
    printf "\n\t Error: cannot use both -p and -l\n"
    usage_display
fi


if [[ ! -z $drive_list ]]; then 
    if [[ ! -z "$unit_start" ]] || [[ ! -z "$unit_end" ]]; then
        printf "\n\t Error: cannot declare -s/-e options with -l \n"
        usage_display
    fi
fi


# FUNCTIONS
################
check_cmds (){
    if [[ ! -e $parted ]]; then 
        printf "\n\t Error: /sbin/parted not found\n\n"
        exit 1
    fi
    if [[ ! -e $mkfs ]]; then 
        printf "\n\t Error: /sbin/mkfs.xfs not found\n\n"
        exit 1
    fi
    if [[ ! -e $sed ]]; then 
        printf "\n\t Error: /bin/sed not found\n\n"
        exit 1
    fi
}

hw_drive_setup() {
    for ((i=unit_start;i<=unit_end;i++)); do
        disk="c"$controller_num"u"$i"p"
        disk_label="c"$controller_num"u"$i
        if [[ ! -e /dev/$disk ]]; then
            printf "\n\t Error: device block does not exist (/dev/$disk) \n"
            exit 1
        fi
        if [[ -z $override ]]; then 
            if [[ $controller_num -eq 0 ]]; then 
                if [[ $unit_start -eq 0 ]]; then 
                    printf "\n\t Error: c0u0p device block is usally the OS device"
                    printf "\n\t        if you are sure you want to start from unit 0"
                    printf "\n\t        please provide the -o option to override this\n"
                fi
            fi
        fi

        $parted -s /dev/$disk mklabel gpt
        sz=$(parted -s /dev/$disk print | grep "Disk"|cut -d ":" -f 2|tr -d " ")
        $parted -s /dev/$disk mkpart primary xfs 0 $sz
        $mkfs -i size=$inode_size -d su=64k,sw=1 -f -L $disk_label /dev/$disk"1"
        mkdir -p /srv/node/$disk_label 
        fstab_line="LABEL=$disk_label /srv/node/$disk_label xfs defaults,noatime,nodiratime,nobarrier,logbufs=8  0  0"
        exists=$(sed -n "/$disk_label xfs/q 2" /etc/fstab  ; echo $?)
        if [[ $exists -ne 2 ]]; then 
            echo "$fstab_line" >> /etc/fstab
        fi
    done
    mount -a
}

vm_drive_setup() {
    for disk in $drive_list; do
        if [[ ! -e /dev/$disk ]]; then
            printf "\n\t Error: device block does not exist (/dev/$disk) \n"
            exit 1
        fi        
        $parted -s /dev/$disk mklabel gpt
        sz=$(parted -s /dev/$disk print | grep "Disk"|cut -d ":" -f 2|tr -d " ")
        $parted -s /dev/$disk mkpart primary xfs 0 $sz
        $mkfs -i size=$inode_size -d su=64k,sw=1 -f -L $disk /dev/$disk"1"
        mkdir -p /srv/node/$disk 
        fstab_line="LABEL=$disk /srv/node/$disk xfs defaults,noatime,nodiratime,nobarrier,logbufs=8  0  0"
        exists=$(sed -n "/$disk xfs/q 2" /etc/fstab  ; echo $?)
        if [[ $exists -ne 2 ]]; then 
            echo "$fstab_line" >> /etc/fstab
        fi        
    done
    mount -a
}

mapper_drive_setup() {
    for ((i=unit_start;i<=unit_end;i++)); do
        disk=${device_prefix}${i}
        disk_label=${disk}
        if [[ ! -e /dev/mapper/$disk ]]; then
            printf "\n\t Error: device block does not exist (/dev/mapper/${disk}) \n"
            exit 1
        fi

        $parted -s /dev/mapper/$disk mklabel gpt
        sz=$(parted -s /dev/mapper/$disk print | grep "Disk"|cut -d ":" -f 2|tr -d " ")
        $parted -s /dev/mapper/$disk mkpart primary xfs 0 $sz
        $mkfs -i size=$inode_size -d su=64k,sw=1 -f -L $disk_label /dev/mapper/$disk"p1"
        mkdir -p /srv/node/$disk_label 
        fstab_line="/dev/mapper/$disk_label-part1 /srv/node/$disk_label xfs defaults,noauto,noatime,nodiratime,nobarrier,logbufs=8  0  0"
        exists=$(sed -n "/$disk_label-part1 xfs/q 2" /etc/fstab  ; echo $?)
        if [[ $exists -ne 2 ]]; then 
            echo "$fstab_line" >> /etc/fstab
        fi
    done
    mount -a
}


# MAIN
##########
check_cmds
if [[ ! -z $controller_num ]]; then 
    hw_drive_setup
fi

if [[ ! -z $drive_list ]]; then 
    vm_drive_setup
fi

if [[ ! -z $device_prefix ]]; then 
    mapper_drive_setup
fi    

printf "\n\n"
exit 0 
