#
#   Author: Marcelo Martins (btorch AT gmail.com)
#   Created: 2011/05/03
#
#   Info:
#       Generates swift cluster configs for the nodes
#       found within the templates directory sctructure
#       This can later be used to be added into a revision
#       control repository
#

cpwd=$(pwd)
base=$(basename $cpwd)
if [[ ! $base =~ ^"swift-setuptools" ]]; then 
    printf "\n Please run the script from its parent directory\n"
    printf "e.g: admin1:~/swift-setuptools.git# ./bin/generate_repo.sh\n"
    exit 1
fi


# Set some variables
setup_conf=$(find . -name "setup_config.cfg") 
repo_module=$(find . -name "repo_setup.sh")
template_dir=$(find . -type d -name "templates")
templates_avail=$(ls -1 $template_dir | grep -v common)
generated_cluster_configs="$HOME/generated_cluster_configs"


# Run some checks
if [[ ! -e $setup_conf ]]; then 
    printf "Error: $setup_conf not found \n\n"
    exit 1
else
    source $setup_conf
fi

if [[ $(cat $setup_conf | grep "account_number") =~ 'account_number=""' ]]; then 
    printf "\nError: config file doesn't seem to have been setup! \n\n"
    exit 1
fi


###############
# FUNCTIONS
###############

# Installs rsync if not present
rsync_check () {
    if [[ ! -e /usr/bin/rsync ]]; then 
        apt-get install rsync -y -qq --force-yes &>/dev/null
    fi
}

# Installs git if not present
git_check () {
    if [[ ! -e /usr/bin/git ]]; then 
        apt-get install git git-core -y -qq --force-yes &>/dev/null
    fi
}

# Replaces the placeholders in the files with the 
# proper values found on setup_config.cfg file
placeholder_changes () {
    loc=$1
    # Mailing Info
    find $loc -iname "aliases" -exec sed -i "s/%EMAIL_ADDR%/$email_addr/" {} \;
    find $loc -iname "aliases" -exec sed -i "s/%PAGER_ADDR%/$pager_addr/" {} \;
    find $loc -iname "update-exim4.conf.conf" -exec sed -i "s/%OUTGOING_DOMAIN%/$outgoing_domain/" {} \;
    find $loc -iname "update-exim4.conf.conf" -exec sed -i "s/%SMARTHOST%/$smarthost/" {} \;
    # Ring Server Changes
    find $loc -iname "ringverify" -exec sed -i "s/%RINGSERVER_IP%/$ringserver_ip/" {} \;
    find $loc -iname "retrievering.sh" -exec sed -i "s/%RINGSERVER_IP%/$ringserver_ip/" {} \;
    # Swift Log Processing Account 
    find $loc -iname "log-processor.conf" -exec sed -i "s/%PROCESSING_ACCOUNT%/$processing_account/" {} \;
    # Swift Hash
    find $loc -iname "swift.conf" -exec sed -i "s/%SWIFT_HASH%/$swift_hash/" {} \;
    # Systlog IP Changes
    find $loc -iname "swift-syslog-ng.conf" -exec sed -i "s/%SYSLOGS_IP%/$syslogs_ip/" {} \;
    # Memcache Changes
    find $loc -iname "memcached.conf" -exec sed -i "s/%MEMCACHE_MAXMEM%/$memcache_maxmem/" {} \;
    find $loc -iname "memcached.conf" -exec sed -i "s/%SIM_CONNECTIONS%/$sim_connections/" {} \;
    find $loc -iname "memcache.conf" -exec sed -i "s/%MEMCACHE_SERVER_LIST%/$memcache_server_list/" {} \;
    # Keystone Changes
    find $loc -iname "proxy-server.conf" -exec sed -i "s/%KEYSTONE_IP%/$keystone_ip/" {} \;
    find $loc -iname "proxy-server.conf" -exec sed -i "s/%KEYSTONE_PORT%/$keystone_port/" {} \;
    find $loc -iname "proxy-server.conf" -exec sed -i "s/%KEYSTONE_AUTH_PROTO%/$keystone_auth_proto/" {} \;
    find $loc -iname "proxy-server.conf" -exec sed -i "s;%KEYSTONE_AUTH_URI%;$keystone_auth_uri;" {} \;
    find $loc -iname "dispersion.conf"   -exec sed -i "s;%KEYSTONE_AUTH_URI%;$keystone_auth_uri;" {} \;
    find $loc -iname "proxy-server.conf" -exec sed -i "s/%KEYSTONE_ADMIN_TENANT%/$keystone_admin_tenant/" {} \;
    find $loc -iname "dispersion.conf"   -exec sed -i "s/%KEYSTONE_ADMIN_TENANT%/$keystone_admin_tenant/" {} \;
    find $loc -iname "proxy-server.conf" -exec sed -i "s/%KEYSTONE_ADMIN_USER%/$keystone_admin_user/" {} \;
    find $loc -iname "dispersion.conf"   -exec sed -i "s/%KEYSTONE_ADMIN_USER%/$keystone_admin_user/" {} \;
    find $loc -iname "proxy-server.conf" -exec sed -i "s/%KEYSTONE_ADMIN_KEY%/$keystone_admin_key/" {} \;
    find $loc -iname "dispersion.conf"   -exec sed -i "s/%KEYSTONE_ADMIN_KEY%/$keystone_admin_key/" {} \;
    # Informant Changes 
    find $loc -iname "proxy-server.conf" -exec sed -i "s/%INFORMANT_IP%/$informant_ip/" {} \;
}

# Generates the configuration files from templates
generate_configs () {
    repo_name="swift-acct$account_number-$account_nick"
    # Check rsync is installed if not do so
    rsync_check

    temp_dir=$(mktemp -d)
    rsync -aq0c --exclude=".ignore" --exclude=".git" $template_dir/ $temp_dir/
    placeholder_changes $temp_dir

    loc_dir="$generated_cluster_configs/$repo_name"
    mkdir -p $loc_dir
    for i in $templates_avail ;
    do
        mkdir $loc_dir/$i
        rsync -aq0c $temp_dir/common/ $loc_dir/$i/ 
        rsync -aq0c $temp_dir/$i/ $loc_dir/$i/ 
    done
    rm -rf $temp_dir

    return 0
}


############
# MAIN 
############
repo_name="swift-acct$account_number-$account_nick"
printf "\n - Generating swift cluster configs:"
if [[ ! -d "$generated_cluster_configs/""$repo_name" ]]; then 
    printf "\n   Account: %s " "$account_number"   
    printf "\n   Customer: %s " "$account_name"   
    printf "\n   Destination: %s/%s " "$generated_cluster_configs" "$repo_name"  

    generate_configs 
    if [[ $? ]]; then 
        printf "\n\n Swift cluster configs have been generated \n\n"
    else 
        printf "\n\n Failed: Swift cluster configs failed to be generated \n\n"
        exit 1
    fi
else
    printf "\n    Path already exists %s/%s " "$generated_cluster_configs" "$repo_name" 
    printf "\n    Skiping generation \n\n"
fi

exit 0 

