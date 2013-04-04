#
#   Author: Marcelo Martins (btorch AT gmail.com)
#   Created: 2013/04/04
#
#   Info:
#       Small script to just do some basic setup 
#       of the admin system. Also syncing the repo
#       files that belong to the admin system over to 
#       root. Please Note: Some cronjobs will be disabled
#       by default which is desired on initial deploy
#

cpwd=$(pwd)
base=$(basename $cpwd)
if [[ ! $base =~ ^"swift-setuptools" ]]; then 
    printf "\n Please run the script from its parent directory\n"
    printf "e.g: admin1:~/swift-setuptools.git# ./bin/setup_adminbox.sh\n"
    exit 1
fi

if [[ $(id -u) -ne 0 ]]; then 
    printf "\n Must be run as root or sudo \n\n"
    exit 1
fi

# Find config
setup_conf=$(find . -name "setup_config.cfg") 

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


#############
# VARIABLES
#############
git_daemon_default="/etc/default/git-daemon"
git_base_dir="/srv/git"
git_repo_name="swift-cluster-configs"
git_repo_loc="$git_base_dir/$git_repo_name.git"


############
# FUNCTIONS
############

apt_install () {
    export DEBIAN_FRONTEND=noninteractive 
    apt-get install -y -qq --force-yes  rsync dsh git git-core \
                                        git-daemon-run nginx \
                                        subversion exim4 \
                                        git-daemon-sysvinit \
                                        syslog-ng &>/dev/null
}

repo_init () {
    cluster_configs="$HOME/generated_cluster_configs/swift-acct$account_number-$account_nick"
    st1=0 ; st2=0 ; st3=0

    if [[ ! -d $cluster_configs ]]; then 
        st1=404 
    fi

    if [[ -d $git_repo_loc ]]; then 
        st2=500
    fi

    if [[ ! -d $git_base_dir ]]; then 
        mkdir $git_base_dir
    fi

    rsync -aq0c --exclude=".git" --exclude=".ignore" $cluster_configs/ $git_repo_loc
    cpwd=$(pwd)
    cd $git_repo_loc
    git init -q
    git add . 
    git commit -q -m "initial commit" -a
    st3=$(git status -s ; echo $?)
    cd $cpwd
    
    ret=$(expr $st1 + $st2 + $st3)
    return $ret
}


###########
# MAIN
###########

printf "\n - Starting AdminBox setup"
printf "\n\t. Installing some utilities"
apt_install
printf "\n\t. Initializing swift-cluster-configs repository"

repo_init
if [[ $? -gt 0 ]]; then 
    printf "\n\tError: git repo initialization not successful (returned code: %s) " "$retc"
    printf "\n\tPath: %s" "$git_repo_loc"
    exit 1
fi

printf "\n\t. Syncing admin configs %s into root / " "$git_repo_loc/admin"
retc=$(rsync -aq0c --exclude=".git" --exclude=".ignore" $git_repo_loc/admin/ / &>/dev/null; echo $?)
if [[ $retc -gt 0 ]]; then 
    printf "\n\tError: rsync issues found\n\n"
    exit 1
fi

printf "\n\t. Setting up & Starting up git-daemon service"
/etc/init.d/git-daemon restart &>/dev/null

printf "\n - AdminBox setup ... Done \n\n"

exit 0 
