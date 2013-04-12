Info on swift-setuptools
=========================

* NOTE:
    - This is a rough draft just to get things going with scripts and modules.
    - On version 2 things will be redesigned and classes added to the modules and creation of a single utility with commands calls
    - Package and repo name will also change

 
Requirements
---------------
* Fabric
* A user (e.g:swiftops) with ssh-key access to all other nodes and sudo privs.
  NOTE: for now the user above (swiftops) needs to have it's own rsa .pub key on it's 
  own authorized_keys to avoid some password calls 
* The storage node must already have all drives attached and available to the system


Swift Environment Assumption
-------------------------------
* A Swift Admin box (MUST HAVE)
* 3 or more swift nodes


Running the scripts
---------------------
After the install you should have the following utilities; swift-adminbox-setup, swift-genconfigs
and swift-node-setup. You should also have a configuration file used by these scripts and template
files for swift systems located under /etc/swift-setuptools directory. You should not modify the
files under the templates directory. After running the swift-genconfigs script there will be a new
location where you will be able check, add, delete, modify the configs, crons, scripts, etc.

#### Order of things:
1. Make sure there is an account (swiftops) that exists on all nodes, has sudo privileges
   and is able to access all other nodes from the admin box using ssh key authentication

2. Create a new /etc/swift-setuptools/swift-setuptools.conf from the swift-setuptools.conf-sample provided

3. Run swift-genconfigs in order to generate the swift environment files from the templates
 * The location /etc/swift-setuptools/generated_cluster_configs will be created

4. Check, Add, Delete, Modify files located under the generated directory above fit your needs

5. Run swift-adminbox-setup to get the admin box ready
   - This will create a git repo from the generated_cluster_configs
   - Sync the admin configs over to the system root
   - Install some packages and startup git-daemon-run, nginx

6. Once the above is done, you can use the swift-node-setup utility to deploy swift nodes.
   The --help can provide some more information and the code itself as well

