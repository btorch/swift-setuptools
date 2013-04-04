#
#   Author: Marcelo Martins (btorch AT gmail.com)
#   Created: 2013/04/04
#
#   Info:
#

cpwd=$(pwd)
base=$(basename $cpwd)
if [[ ! $base =~ ^"swift-setuptools" ]]; then 
    printf "\n Please run the script from its parent directory\n"
    printf "e.g: admin1:~/swift-setuptools.git# ./bin/setup_adminbox.sh\n"
    exit 1
fi


# Set some variables
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



###########
# MAIN
###########

# Install some tools now
export DEBIAN_FRONTEND=noninteractive 
apt-get install -y -qq --force-yes  rsync dsh git git-core \
                                    git-daemon-runnginx \
                                    subversion exim4 \
                                    git-daemon-sysvinit \
                                    syslog-ng &>/dev/null

# Setup the git repository & git-daemon
git_daemon_default="/etc/default/git-daemon"
git_base_dir="/srv/git"
git_repo_name="swift-cluster-configs"
git_repo_loc="$git_base_dir/$git_repo_name"

# Modify git-daemon files & start service
sed -i 's;GIT_DAEMON_ENABLE=false;GIT_DAEMON_ENABLE=true;' $git_daemon_default
sed -i 's;GIT_DAEMON_DIRECTORY=/var/cache/git;GIT_DAEMON_DIRECTORY=/srv/git;' $git_daemon_default
sed -i 's;GIT_DAEMON_OPTIONS="";GIT_DAEMON_OPTIONS="--syslog --detach --export-all --max-connections=0";' $git_daemon_default
echo "GIT_DAEMON_BASE_PATH=/srv/git" >> $git_daemon_default


if [[ ! -d $git_repo_loc ]]; then 
    mkdir -p $git_repo_loc.git
fi



# - sync tempaltes over to git repo location
# - Then
#   git init
#   git add . 
#   git commit -m "initial commit" -a

# Now let's rsync the repo
rsync -aq0c --exclude=".git" $git_dir/admin /



printf "\n - Generating swift config repo"
if [[ ! -d "$git_dir""$git_repo_name" ]]; then 
    printf "\n   Destination: %s%s \n" "$git_dir" "$git_repo_name"  
    generate_git_repo 
    if [[ $? ]]; then 
        printf "\n   Git repo has been created and initialized with success"
        printf "\n   Please review the configuration files genrated for any"
        printf "\n   further desired changes \n\n"
    else 
        printf "\n   Git repo generation FAILED \n\n"
        exit 1
    fi
else
    printf "\n   Path /srv/git/swift-acct$account_number-$account_nick already exists"
    printf "\n   Not doing anything \n\n"
fi

exit 0 
