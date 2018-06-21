import shutit

# This creates a box that speeds up builds for https://github.com/ianmiell/shutit-openshift-cluster

#s = shutit.create_session('bash',loglevel='debug',echo=True)
s = shutit.create_session('bash',loglevel='info',echo=True)
s.send('rm -rf tmpvagrantboxcreate && mkdir tmpvagrantboxcreate && cd tmpvagrantboxcreate')
s.send('vagrant init centos/7')
s.send('vagrant box update')
s.send('vagrant up')

# Log onto machine and prepare it.
s.login('vagrant ssh')
s.login('sudo su -')
s.pause_point('')
s.send('yum install -y wget')
# Not necessary, but handy
s.install('yum-utils')
s.install('sysstat')
# Installed by cookbook anyway
s.install('epel-release')
s.install('docker')
s.install('iptables-services')
s.install('vim-enhanced')
s.install('git')
s.install('dnsmasq')
s.install('python')
s.install('libselinux-python')
s.install('net-tools')
s.install('bind-utils')
s.install('bash-completion')
s.install('deltarpm')
s.install('libselinux-python')
# origin deps TODO
#s.multisend('yum install -y ',{'s this ok':'y'})

s.send(r'''sed -i 's/.*\/10\(.*\)/*\1/' /etc/cron.d/sysstat && systemctl enable sysstat''')
s.send(r'''sed -i 's/^\(127.0.0.1[ \t]*[^ \t]*\).*/\1/' /etc/hosts''',note='Make sure chef sees a fqdn.')
s.send('wget -qO- https://raw.githubusercontent.com/ianmiell/vagrant-swapfile/master/vagrant-swapfile.sh | sh')
s.send('echo root:origin | /usr/sbin/chpasswd')

# Downloads
s.send('wget -nc -q https://packages.chef.io/files/stable/chef/13.5.3/el/7/chef-13.5.3-1.el7.x86_64.rpm')
#s.send('wget -nc -q https://packages.chef.io/files/stable/chef/12.21.4/el/7/chef-12.21.4-1.el7.x86_64.rpm')
s.send('wget -nc -q https://packages.chef.io/files/stable/chefdk/1.6.1/el/7/chefdk-1.6.1-1.el7.x86_64.rpm')
# Go to chef website and download the rpm. Then split and store on github, and pull from the raw links here.
#eg:
# split -b 49m chef-server-core-12.17.3-1.el7.x86_64.rpm chef-server-core-12.17.3-1.el7.x86_64.rpm.x
s.send('wget -nc -q https://github.com/ianmiell/shutit-chef-env/raw/master/chef-server-core-12.17.3-1.el7.x86_64.rpm.xaa')
s.send('wget -nc -q https://github.com/ianmiell/shutit-chef-env/raw/master/chef-server-core-12.17.3-1.el7.x86_64.rpm.xab')
s.send('wget -nc -q https://github.com/ianmiell/shutit-chef-env/raw/master/chef-server-core-12.17.3-1.el7.x86_64.rpm.xac')
s.send('cat chef-server-core-12.17.3-1.el7.x86_64.rpm.xaa chef-server-core-12.17.3-1.el7.x86_64.rpm.xab chef-server-core-12.17.3-1.el7.x86_64.rpm.xac > chef-server-core-12.17.3-1.el7.x86_64.rpm')
s.send('rm -f *xaa *xab *xac')

# Guest additions
s.multisend('yum install -y dkms kernel-devel kernel-devel-3.10.0-693.17.1.el7.x86_64',{'s this ok':'y'})
s.multisend('yum groupinstall "Development Tools"',{'s this ok':'y'})
s.send('wget -q http://download.virtualbox.org/virtualbox/5.2.2/VBoxGuestAdditions_5.2.2.iso')
s.send('mount -t iso9660 -o loop ./VBoxGuestAdditions_*.iso /mnt')
s.send('cd /mnt')
s.send('./VBoxLinuxAdditions.run')
s.send('cd -')


# Workaround for docker networking issues + landrush.
s.insert_text('Environment=GODEBUG=netdns=cgo','/lib/systemd/system/docker.service',pattern='.Service.')
s.send('mkdir -p /etc/docker',note='Create the docker config folder')
# The containers running in the pods take their dns setting from the docker daemon. Add the default kubernetes service ip to the list so that items can be updated.
# Ref: IWT-3895
#s.send_file('/etc/docker/daemon.json',"""{
#  "dns": ["8.8.8.8"]
#}""",note='Use the google dns server rather than the vagrant one. Change to the value you want if this does not work, eg if google dns is blocked.')

                                                      
s.send(r'''sed -i 's/^\(127.0.0.1[ \t]*[^ \t]*\).*/\1/' /etc/hosts''')                                                                                           
s.send('''sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config''')                                                              
s.send('''sed -i 's/.*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config''')                                                                           
s.send('service sshd restart')                                                                                                                                   
s.send('echo root:chef | /usr/sbin/chpasswd')                                                                                                      
s.multisend('ssh-keygen',{'Enter file':'','Enter passphrase':'','Enter same pass':''})  
# install expects httpd to be not installed
#s.install('httpd')
s.remove('httpd')
s.send('touch /root/buildtime')
s.logout()
s.logout()

# Remove package.box because it's hella confusing otherwise.
s.send('vagrant box remove package.box || true')
s.send('vagrant package')
s.send('split -b 49m package.box') # 50m is the github warning limit
s.send('cd /space/git/shutit-openshift-cluster')
s.send('rm -rf cachedbox/* || git rm -f cachedbox/*')
s.send('mkdir -p /space/git/shutit-openshift-cluster/cachedbox')
s.send('cd -')
s.send('mv x* /space/git/shutit-openshift-cluster/cachedbox')
s.send('cd /space/git/shutit-openshift-cluster')
s.send('git add cachedbox')
s.send('git commit -am cachedbox')
s.send('git push')
s.send('cd -')

s.pause_point('Box created.')
