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
#   On a VM system, it's a whole other story and therefore a drive_regex
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
    sudo setup_drives.sh [-V -r drive_regex] [-o] | [-c num -s num -e num] [-o]
        -V  Indicates you are setting them up on a Virtual Instance
        -r  Regex used for figuring out devices to use (USE double quotes)
        -c  Controller nummber in case you are using the cXuYp udev formatting 
        -s  The first unit to start the drive setup from
        -e  The last unit that the drive setup will run on
        -o  Allows the override and will partition and format c0u0p (BeCareful: ususally OS drive)
        -h For this usage screen

    NOTE: The -c/-s/-e options cannot be used when -V is declared

USAGE
exit 1
}


# Parsing arguments
while getopts "Vor:c:s:e:h" opts
do
    case $opts in         
        V)
            vm_use=1
        ;;
        o)
            override=1
        ;;
        r)
            drive_regex="${OPTARG}"
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
if [[ $num_of_args -lt 3 ]]; then 
    printf "\n\t Error: Must have at least 2 arguments given\n"
    usage_display
fi

# Checking ARGS passed
if [[ -z "$vm_use" ]] && [[ ! -z $drive_regex ]]; then 
    printf "\n\t Error: Both -V and -r must be provided\n"
    usage_display
fi
if [[ ! -z "$vm_use" ]] && [[ -z $drive_regex ]]; then 
    printf "\n\t Error: Both -V and -r must be provided\n"
    usage_display
fi
if [[ ! -z "$vm_use" ]] && [[ ! -z $drive_regex ]]; then 
    if [[ ! -z "$controller_num" ]] || [[ ! -z "$unit_start" ]] || [[ ! -z "$unit_end" ]]; then
        printf "\n\t Error: Cannot declare -c/-s/-e options with -V and -r \n"
        usage_display
    fi
fi
if [[ -z "$controller_num" ]] || [[ -z "$unit_start" ]] || [[ -z "$unit_end" ]]; then
    if [[ -z "$vm_use" ]] && [[ -z $drive_regex ]]; then 
        printf "\n\t Error: All following options must be declared -c/-s/-e\n"
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

hw_system_setup (){
    for ((i=unit_start;i<=unit_end;i++)); do
        if [[ ! -e /dev/c"$controller_num"u"$i"p ]]; then
            printf "\n\t Error: device block does not exist (/dev/c"$controller_num"u"$i"p) \n"
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

        $parted -s /dev/c"$controller_num"u"$i"p mklabel gpt
        sz=$(parted -s /dev/c"$controller_num"u"$i"p print | grep "Disk"|cut -d ":" -f 2|tr -d " ")
        $parted -s /dev/c"$controller_num"u"$i"p mkpart primary xfs 0 $sz
        $mkfs -i size=$inode_size -d su=64k,sw=1 -f -L c"$controller_num"u"$i" /dev/c"$controller_num"u"$i"p1
        mkdir -p /srv/node/c"$controller_num"u"$i" 
        fstab_line="LABEL=c"$controller_num"u"$i" /srv/node/c"$controller_num"u"$i" xfs defaults,noatime,nodiratime,nobarrier,logbufs=8  0  0"
        echo "$fstab_line" >> /etc/fstab
    done
}


# MAIN
##########
check_cmds
if [[ -z $vm_use ]]; then 
    hw_system_setup
fi

if [[ ! -z $vm_use ]]; then 
    printf "\n\t Not yet implemented"
fi

printf "\n\n"
exit 0 