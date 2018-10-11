import random
import datetime
import inspect
import string
import os
import importlib
import logging
import sys
import time
import jinja2
from library import check_nodes
from library import cluster_test
from library import controller
from library import crd
from library import istio
from library import test_reset
from library import test_uninstall
from library import upgrades
from library import vault
from library import run_apps

from shutit_module import ShutItModule

class shutit_openshift_cluster(ShutItModule):

	def build(self, shutit):

		################################################################################
		# SERVICE FUNCTIONS
		def check_version(shutit, check_version):
			version = shutit.send_and_get_output(r"""oc version | grep -w oc | awk '{print $2}' | sed 's/.\([0-9]*\.[0-9]*\).*/\1/'""")
			return version == check_version

		def get_cookbooks(shutit, shutit_session):
			if shutit.cfg[self.module_id]['chef_docker_cookbook_version'] == 'latest':
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/docker/versions/latest/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			else:
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/docker/versions/'+ shutit.cfg[self.module_id]['chef_docker_cookbook_version'] + '/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			if shutit.cfg[self.module_id]['chef_iptables_cookbook_version'] == 'latest':
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/iptables/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			else:
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/iptables/versions/'+ shutit.cfg[self.module_id]['chef_iptables_cookbook_version'] + '/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			if shutit.cfg[self.module_id]['chef_yum_cookbook_version'] == 'latest':
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/yum/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			else:
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/yum/versions/'+ shutit.cfg[self.module_id]['chef_yum_cookbook_version'] + '/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			if shutit.cfg[self.module_id]['chef_selinux_policy_cookbook_version'] == 'latest':
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/selinux_policy/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			else:
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/selinux_policy/versions/'+ shutit.cfg[self.module_id]['chef_selinux_policy_cookbook_version'] + '/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			if shutit.cfg[self.module_id]['chef_compat_resource_cookbook_version'] == 'latest':
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/compat_resource/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			else:
				shutit_session.send('curl -L https://supermarket.chef.io/cookbooks/compat_resource/versions/'+ shutit.cfg[self.module_id]['chef_compat_resource_cookbook_version'] + '/download | tar -zxvf -',note='Get cookbook dependencies',background=True,wait=False,block_other_commands=False)
			shutit_session.wait()

		# Wait for all sessions to complete
		def sync(test_config_module, shutit_sessions):
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.wait()

		# For 3.7 upgrade, docker upgrade requires a redeploy to ensure all is ok
		def redeploy_components(shutit_session):
			shutit_session.send('oc rollout latest docker-registry')
			shutit_session.send('oc rollout latest router')
			# Dumbly wait a minute
			shutit_session.send('sleep 60')
		################################################################################


		################################################################################
		# Extract password from 'secret' file (which git ignores).
		# TODO: check perms are only readable by user
		try:
			pw = open('secret').read().strip()
		except IOError:
			pw = ''
		if pw == '':
			shutit.log('''================================================================================\nWARNING! IF THIS DOES NOT WORK YOU MAY NEED TO SET UP A 'secret' FILE IN THIS FOLDER!\n================================================================================''',level=logging.CRITICAL)
			pw='nopass'
		################################################################################

		################################################################################
		# Config
		vagrant_image    = shutit.cfg[self.module_id]['vagrant_image']
		try:
			is_interactive = sys.stdout.isatty() or os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno())
		except OSError:
			is_interactive = False
		################################################################################


		################################################################################
		# VAGRANT UP
		# Collect the - expect machines dict to be set up here
		vagrantcommand = 'vagrant'
		test_config_module = importlib.import_module('cluster_configs.' + shutit.cfg[self.module_id]['test_config_dir'] + '.machines_' + shutit.cfg[self.module_id]['chef_deploy_method'])
		self_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0)))
		shutit.cfg[self.module_id]['vagrant_run_dir'] = self_dir + '/vagrant_run'
		run_dir = shutit.cfg[self.module_id]['vagrant_run_dir']
		timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		module_name = shutit.cfg[self.module_id]['cluster_vm_names'] + '_' + timestamp
		shutit_sessions = {}
		# Set up provider.
		if shutit.cfg[self.module_id]['vagrant_provider'] == 'virtualbox':
			if shutit.send_and_get_output('vagrant plugin list 2>/dev/null | grep libvirt | wc -l') != '0':
				shutit.cfg[self.module_id]['vagrant_provider'] = 'libvirt'
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		shutit.send('command rm -rf ' + run_dir + '/' + module_name + ' && command mkdir -p ' + run_dir + '/' + timestamp + ' && command cd ' + run_dir + '/' + timestamp)
		if vagrant_provider == 'virtualbox':
			shutit.send('cat ' + self_dir + '/cachedbox/x* > ' + run_dir + '/' + timestamp + '/' + vagrant_image)
		elif vagrant_provider == 'libvirt':
			shutit.send('cat ' + self_dir + '/cachedbox_libvirt/x* > ' + run_dir + '/' + timestamp + '/' + vagrant_image)
		else:
			shutit.fail('Vagrant provider not supported: ' + vagrant_provider)
		if shutit.send_and_get_output(vagrantcommand + ' plugin list | grep landrush') == '':
			shutit.multisend(vagrantcommand + ' plugin install landrush',{'assword':pw})
		if vagrant_provider == 'virtualbox' and shutit.send_and_get_output('ifconfig vboxnet0 2> /dev/null | wc -l') != '0':
			shutit.send('VBoxManage hostonlyif remove vboxnet0',note='''If this is not performed, then landrush will eventually run out of IPs on the subnet. Vagrant recreates the vboxnet0 interface as needed.''')
		shutit.multisend(vagrantcommand + ' init && rm -f Vagrantfile',{'assword':pw})
		template = jinja2.Template(open(self_dir + '/cluster_configs/' + shutit.cfg[self.module_id]['test_config_dir'] + '/Vagrantfile.' + shutit.cfg[self.module_id]['chef_deploy_method']).read())
		shutit.send_file(run_dir + '/' + timestamp + '/Vagrantfile',str(template.render(vagrant_image='file://./' + vagrant_image,cfg=shutit.cfg[self.module_id])))
		################################################################################

		################################################################################
		# Set up the sessions
		for machine in test_config_module.machines.keys():
			shutit_sessions.update({machine:shutit.create_session(session_type='bash', loglevel='debug', nocolor=True)})
		################################################################################

		################################################################################
		# Set up vagrant machines and sessions and validate landrush
		for machine in test_config_module.machines.keys():
			shutit_session = shutit_sessions[machine]
			shutit_session.send('cd ' + run_dir + '/' + timestamp)
			# Remove any existing landrush entry.
			shutit_session.send(vagrantcommand + ' landrush rm ' + test_config_module.machines[machine]['fqdn'])
			# vagrant up - Needs to be done serially for stability reasons.
			shutit_session.multisend(vagrantcommand + ' up --provider ' + vagrant_provider + ' ' + machine,{'assword for':pw})
			# Check that the landrush entry is there.
			shutit_session.send(vagrantcommand + ' landrush ls | grep -w ' + test_config_module.machines[machine]['fqdn'])
			shutit_session.login(command=vagrantcommand + ' ssh ' + machine)
			shutit_session.login(command='sudo su - ')
			shutit_session.send(r'''cat <(echo -n $(ip -4 -o addr show scope global | grep -v 10.0.2.15 | head -1 | awk '{print $4}' | sed 's/\(.*\)\/.*/\1/') $(hostname)) <(echo) <(cat /etc/hosts | grep -v $(hostname -s)) > /tmp/hosts && mv -f /tmp/hosts /etc/hosts''')
			# Correct any broken ip addresses.
			if shutit.send_and_get_output('''vagrant landrush ls | grep ''' + machine + ''' | grep 10.0.2.15 | wc -l''') != '0':
				shutit.log('A 10.0.2.15 landrush ip was detected for machine: ' + machine + ', correcting.',level=logging.WARNING)
				# This beaut gets all the eth0 addresses from the machine and picks the first one that it not 10.0.2.15.
				while True:
					ipaddr = shutit_session.send_and_get_output(r"""ip -4 -o addr show scope global | grep -v 10.0.2.15 | head -1 | awk '{print $4}' | sed 's/\(.*\)\/.*/\1/'""")
					if ipaddr[0] not in ('1','2','3','4','5','6','7','8','9'):
						time.sleep(10)
					else:
						break
				# Send this on the host (shutit, not shutit_session)
				shutit.send('vagrant landrush set ' + test_config_module.machines[machine]['fqdn'] + ' ' + ipaddr)
			test_config_module.machines[machine]['interface'] = shutit_session.send_and_get_output(r"ip -4 -o addr show scope global | grep -v 10.0.2.15 | awk '{print $2}' | head -1")
			test_config_module.machines[machine]['ipaddress']  = shutit_session.send_and_get_output(r"""ip -4 -o addr show scope global | grep -v 10.0.2.15 | head -1 | awk '{print $4}' | sed 's/\(.*\)\/.*/\1/'""")
			test_config_module.machines[machine]['macaddress'] = shutit_session.send_and_get_output('ip addr show ' + test_config_module.machines[machine]['interface'] + r""" | grep -w link.ether | awk '{print $2}'""").upper()
		# Gather landrush info
		for machine in sorted(test_config_module.machines.keys()):
			ip = shutit.send_and_get_output(vagrantcommand + ''' landrush ls 2> /dev/null | grep -w ^''' + test_config_module.machines[machine]['fqdn'] + ''' | awk '{print $2}' ''')
			test_config_module.machines.get(machine).update({'ip':ip})
		###############################################################################

		###############################################################################
		# Set root password
		root_pass = 'chef'
		###############################################################################

		###############################################################################
		# Set up hosts for chef appropriate for their role
		for machine in sorted(test_config_module.machines.keys()):
			shutit_session = shutit_sessions[machine]
			# Set root password
			shutit_session.send('echo root:' + root_pass + ' | /usr/sbin/chpasswd')
			shutit_session.send('cd /root')
			if test_config_module.machines[machine]['fqdn'] in ('chefwkstn.vagrant.test',) and shutit.cfg[self.module_id]['chef_deploy_method'] == 'server':
				shutit_session.send('rpm -i chefdk-*.el7.x86_64.rpm',background=True,wait=False,block_other_commands=False)
			elif test_config_module.machines[machine]['fqdn'] in ('chefserver.vagrant.test',) and shutit.cfg[self.module_id]['chef_deploy_method'] == 'server':
				shutit_session.send('rpm -i chef-server-core*.rpm && chef-server-ctl reconfigure && chef-server-ctl install chef-manage',note='Install chef manager',background=True,wait=False,block_other_commands=False)
		###############################################################################

		###############################################################################
		# Go on each machine and copy ssh ids so we can move between hosts without passwords.
		if is_interactive:
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				for to_machine in sorted(test_config_module.machines.keys()):
					shutit_session.multisend('ssh-copy-id root@' + to_machine + '.vagrant.test',{'ontinue connecting':'yes','assword':root_pass})
					shutit_session.multisend('ssh-copy-id root@' + to_machine,{'ontinue connecting':'yes','assword':root_pass})
		###############################################################################

		###############################################################################
		# Wait for completion of installs above
		sync(test_config_module, shutit_sessions)
		###############################################################################

		###############################################################################
		# Set up shortcuts to sessions
		if shutit.cfg[self.module_id]['chef_deploy_method'] == 'server':
			shutit_chefserver_session = shutit_sessions['chefserver']
			shutit_chefwkstn_session = shutit_sessions['chefwkstn']
		else:
			shutit_chefserver_session = None
			shutit_chefwkstn_session = None
		shutit_master1_session = shutit_sessions['master1']
		###############################################################################


		###############################################################################
		# Set up chef server
		if shutit.cfg[self.module_id]['chef_deploy_method'] == 'server':
			shutit_chefserver_session.send("""chef-server-ctl user-create admin admin admin admin@example.com examplepass -f admin.pem""",note='Create the admin user certificate')
			shutit_chefserver_session.send("""chef-server-ctl org-create mycorp "MyCorp" --association_user admin -f mycorp-validator.pem""",note='Create the organisation validator certificate')
			admin_pem = shutit_chefserver_session.send_and_get_output('cat admin.pem')
			validator_pem = shutit_chefserver_session.send_and_get_output('cat mycorp-validator.pem')

			# Knife file
			knife_rb_file = '''current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "admin"
client_key               "#{current_dir}/admin.pem"
validation_client_name   "mycorp-validator"
validation_key           "#{current_dir}/mycorp-validator.pem"
chef_server_url          "https://chefserver.vagrant.test/organizations/mycorp"
syntax_check_cache_path  "#{ENV['HOME']}/.chef/syntaxcache"
cookbook_path            ["#{current_dir}/../cookbooks"]'''

			# Set up chef workstation
			shutit_chefwkstn_session.send('git config --global user.name "Your Name"')
			shutit_chefwkstn_session.send('git config --global user.email "username@domain.com"')
			shutit_chefwkstn_session.send('cd /root')
			shutit_chefwkstn_session.send('chef generate repo chef-repo')
			shutit_chefwkstn_session.send('cd /root/chef-repo')
			shutit_chefwkstn_session.send('''echo 'eval "$(chef shell-init bash)"' >> /root/.bash_profile''')
			shutit_chefwkstn_session.send('source /root/.bash_profile')
			shutit_chefwkstn_session.send('mkdir -p /etc/chef')
			shutit_chefwkstn_session.send('mkdir -p /root/.chef')
			shutit_chefwkstn_session.send_file('/etc/chef/admin.pem',admin_pem)
			shutit_chefwkstn_session.send_file('/root/.chef/admin.pem',admin_pem)
			shutit_chefwkstn_session.send_file('/etc/chef/mycorp-validator.pem',validator_pem)
			shutit_chefwkstn_session.send_file('/etc/chef/client.rb',knife_rb_file)
			shutit_chefwkstn_session.send_file('/root/.chef/knife.rb',knife_rb_file)
			shutit_chefwkstn_session.send('knife ssl fetch')
		###############################################################################


		###############################################################################
		# Install chef all all hosts except chef ones
		for machine in sorted(test_config_module.machines.keys()):
			# Do not run this on the chef machines we've handled above
			if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
				shutit_session = shutit_sessions[machine]
				# Set up host as a chef node
				if test_config_module.machines[machine]['is_node']:
					pass
					#shutit_session.send('docker pull mysql',background=True,wait=False,block_other_commands=False)
				shutit_session.send('rpm -i chef-13.5.3-1.el7.x86_64.rpm',background=True,wait=False,block_other_commands=False)
				shutit_session.send('mkdir -p /etc/chef',background=True,wait=False,block_other_commands=False)
				shutit_session.send('mkdir -p /root/.chef',background=True,wait=False,block_other_commands=False)
		# Wait for completion
		sync(test_config_module, shutit_sessions)
		if shutit.cfg[self.module_id]['chef_deploy_method'] == 'server':
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					shutit_session = shutit_sessions[machine]
					shutit_session.send_file('/root/.chef/knife.rb',knife_rb_file)
					shutit_session.send_file('/root/.chef/admin.pem',admin_pem)
		for machine in sorted(test_config_module.machines.keys()):
			if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
				shutit_session = shutit_sessions[machine]
				f          = '/opt/chef/embedded/lib/ruby/gems/2.4.0/gems/ohai-13.5.0/lib/ohai/plugins/linux/network.rb'
				shutit_session.send(r'''sed -i 's/\(.*ipaddress \).*/\1 "''' + test_config_module.machines[machine]['ipaddress'] + '''"/' ''' + f)
				shutit_session.send(r'''sed -i 's/\(.*macaddress m\).*/\1 "''' + test_config_module.machines[machine]['macaddress'] + '''"/' ''' + f)
		if shutit.cfg[self.module_id]['chef_deploy_method'] == 'server':
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					shutit_session.send('knife ssl fetch')
					fqdn = test_config_module.machines[machine]['fqdn']
					shutit_session.multisend('knife bootstrap -N ' + fqdn + ' ' + fqdn,{'Node ' + fqdn + ' exists, overwrite it':'Y','Client ' + fqdn + ' exists, overwrite it':'Y','assword:':root_pass})
		###############################################################################

		###############################################################################
		# chef-solo method
		if shutit.cfg[self.module_id]['chef_deploy_method'] == 'solo':
			# Check out cookbook on all hosts
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					shutit_session.send('cd /root')
					#shutit_session.send('git clone https://github.com/openshift/svt',background=True,wait=False,block_other_commands=False)
					#shutit_session.send('git clone https://github.com/openshift/origin',background=True,wait=False,block_other_commands=False)
					shutit_session.send('mkdir -p /root/chef-solo-example /root/chef-solo-example/cookbooks /root/chef-solo-example/environments /root/chef-solo-example/logs',note='Create chef folders')
					shutit_session.send('cd /root/chef-solo-example/cookbooks')
					shutit_session.send('git clone https://github.com/IshentRas/cookbook-openshift3',note='Clone chef repo')
					shutit_session.send('cd cookbook-openshift3',note='mv into dir')
					shutit_session.send('git checkout ' + shutit.cfg[self.module_id]['cookbook_branch'],note='Checkout chef repo')
					shutit_session.send('cd ..',note='Revert dir')
			# Wait for completion
			sync(test_config_module, shutit_sessions)
			# Correct the dependencies
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					shutit_session.send('cd /root/chef-solo-example/cookbooks/cookbook-openshift3')
					if shutit.cfg[self.module_id]['inject_compat_resource']:
						shutit_session.send("""echo "depends 'compat_resource'" >> metadata.rb""")
					## Test json validity in github code - not sure this works.
					#shutit_session.send(r"find .|grep json$|sed 's/.*/echo \0 \&\& cat \0 | python -m json.tool > \/dev\/null/'|sh",background=True,wait=False,block_other_commands=False)
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					shutit_session.send('cd /root/chef-solo-example/cookbooks')
					if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
						get_cookbooks(shutit, shutit_session)
			# Wait for completion
			sync(test_config_module, shutit_sessions)

			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					# Create solo.rb
					template = jinja2.Template(open(self_dir + '/cluster_configs/' + shutit.cfg[self.module_id]['test_config_dir'] + '/solo.rb').read())
					shutit_session.send_file('/root/chef-solo-example/solo.rb',str(template.render()),note='Create solo.rb file')
					# Create environment file
					template = jinja2.Template(open(self_dir + '/cluster_configs/' + shutit.cfg[self.module_id]['test_config_dir'] + '/environment.json').read())
					shutit_session.send_file('/root/chef-solo-example/environments/ocp-cluster-environment.json',str(template.render(test_config_module=test_config_module,cfg=shutit.cfg[self.module_id])),note='Create environment file')
					shutit_session.send(r'''echo '*/5 * * * * PATH=${PATH}:/usr/sbin chef-solo --run-lock-timeout 0 --environment ocp-cluster-environment -o '"'"'recipe[cookbook-openshift3]'"'"' -c ~/chef-solo-example/solo.rb > /tmp/chef.log.`date "+\%s"` 2>&1' | crontab''',note='set up crontab on ' + machine)
					shutit_session.send(r'''chef-solo --run-lock-timeout 0 --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb >> /tmp/chef.log.`date "+%s"` 2>&1 || true''',background=True,wait=False,block_other_commands=False)
		# chef-server method
		else:
			shutit_chefwkstn_session.send('mkdir -p /root/chef-repo/cookbooks')
			shutit_chefwkstn_session.send('cd /root/chef-repo/cookbooks')
			get_cookbooks(shutit, shutit_chefwkstn_session)

			# Get the community cookbook in
			shutit_chefwkstn_session.send('git clone -b ' + shutit.cfg[self.module_id]['cookbook_branch'] + ' https://github.com/IshentRas/cookbook-openshift3',note='Clone chef repo',background=True,wait=False,block_other_commands=False)
			if shutit.cfg[self.module_id]['inject_compat_resource']:
				shutit_chefwkstn_session.send("""echo "depends 'compat_resource'" >> metadata.rb""",background=True,wait=False,block_other_commands=False)
			shutit_chefwkstn_session.send('cd /root/chef-repo')
			# Wait for downloads to complete
			shutit_chefwkstn_session.wait()

			# This can fail if there is a dep error! Need to confirm 'Uploaded' was in the output.
			# TODO: background and sync
			shutit_chefwkstn_session.send_until('knife cookbook upload -o $(pwd)/cookbooks iptables','.*Uploaded.*')
			shutit_chefwkstn_session.send_until('knife cookbook upload -o $(pwd)/cookbooks yum','.*Uploaded.*')
			shutit_chefwkstn_session.send_until('knife cookbook upload -o $(pwd)/cookbooks compat_resource','.*Uploaded.*')
			shutit_chefwkstn_session.send_until('knife cookbook upload -o $(pwd)/cookbooks selinux_policy','.*Uploaded.*')
			shutit_chefwkstn_session.send_until('knife cookbook upload -o $(pwd)/cookbooks docker','.*Uploaded.*')
			shutit_chefwkstn_session.send_until('knife cookbook upload -o $(pwd)/cookbooks cookbook-openshift3','.*Uploaded.*')

			# Create role file
			shutit_chefwkstn_session.send('mkdir -p /root/chef-repo/cookbooks/cookbook-openshift3/roles')
			for f in ('role.json','testcluster1_openshift_etcd_duty.json','testcluster1_openshift_first_etcd_duty.json','testcluster1_openshift_first_master_duty.json','testcluster1_openshift_master_duty.json','testcluster1_openshift_node_duty.json','testcluster1_use_role_based_duty_discovery.json','testcluster1_openshift_certificate_server_duty.json','testcluster1_openshift_lb_duty.json'):
				template = jinja2.Template(open(self_dir + '/cluster_configs/' + shutit.cfg[self.module_id]['test_config_dir'] + '/' + f).read())
				shutit_chefwkstn_session.send_file('/root/chef-repo/cookbooks/cookbook-openshift3/roles/' + f,str(template.render(test_config_module=test_config_module,cfg=shutit.cfg[self.module_id])),note='Create role.json file')
				shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/' + f)
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')

			# Assign roles to nodes in run_lists
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[role]'")
					shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_use_role_based_duty_discovery]'")
					# Assign appropriate roles to appropriate nodes.
					if test_config_module.machines[machine]['is_master']:
						shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_openshift_master_duty]'")
					if test_config_module.machines[machine]['is_first_master']:
						shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_openshift_first_master_duty]'")
					if test_config_module.machines[machine]['is_etcd']:
						shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_openshift_etcd_duty]'")
					if test_config_module.machines[machine]['is_first_etcd']:
						shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_openshift_first_etcd_duty]'")
					if test_config_module.machines[machine]['is_node']:
						shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_openshift_node_duty]'")
					if test_config_module.machines[machine]['is_certificate_server']:
						shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_openshift_certificate_server_duty]'")
					if test_config_module.machines[machine]['is_lb']:
						shutit_chefwkstn_session.send('knife node run_list add ' + test_config_module.machines[machine]['fqdn'] + " 'role[testcluster1_openshift_lb_duty]'")

			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['fqdn'] not in ('chefserver.vagrant.test','chefwkstn.vagrant.test'):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r'''echo '*/5 * * * * PATH=${PATH}:/usr/sbin chef-client --run-lock-timeout 0 > /tmp/chef.log.`date "+\%s"` 2>&1' | crontab''',note='set up crontab on ' + machine)
		###############################################################################

		check_nodes.check_nodes(shutit_master1_session, test_config_module, vagrantcommand, vagrant_provider, pw)
		shutit_master1_session.send('systemctl stop crond')
		check_nodes.label_nodes(shutit_master1_session, test_config_module)

		run_apps.do_run_apps(test_config_module, shutit_master1_session, shutit, shutit_session)

		# Test cluster
		cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)

		# Ad hoc uninstall
		if shutit.cfg[self.module_id]['do_adhoc_uninstall']:
			test_uninstall.do_uninstall(shutit, test_config_module, shutit_sessions, shutit.cfg[self.module_id]['chef_deploy_method'])
			cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)

		# Ad hoc reset
		if shutit.cfg[self.module_id]['do_adhoc_reset']:
			test_reset.do_reset(test_config_module, shutit_sessions, shutit.cfg[self.module_id]['chef_deploy_method'])
			cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)


		# Istio
		if shutit.cfg[self.module_id]['do_istio']:
			istio.install_istio(shutit_master1_session)

		# Vault
		if shutit.cfg[self.module_id]['do_vault']:
			vault.do_vault(shutit_master1_session)

		# CRD
		if shutit.cfg[self.module_id]['do_crd']:
			crd.do_crd_simple(shutit_master1_session)

		# Upgrades
		upgrades.do_upgrades(shutit,
		                     test_config_module,
		                     shutit_sessions,
		                     check_version,
		                     shutit_chefwkstn_session,
		                     shutit_master1_session,
		                     self.module_id)

		# Diagnostic tests
		cluster_test.diagnostic_tests(shutit_master1_session)

		# User access
		shutit.pause_point('Build complete and passed OK - interactive access now granted.')

		# CLEANUP
		shutit.send(vagrantcommand + ' halt || true',note='Best effort halt and destroy')
		shutit.send(vagrantcommand + ' destroy -f || true',note='Best effort destroy')
		return True


	def get_config(self, shutit):
		# See https://github.com/ianmiell/shutit-scripts/vagrant-box-create for the creation of ianmiell/centos7ose
		#shutit.get_config(self.module_id,'vagrant_image',default='centos/7')
		shutit.get_config(self.module_id,'vagrant_image',default=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))+'.box')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		# Vagrantfile and environment files in here
		shutit.get_config(self.module_id,'test_config_dir',default='test_multi_node_basic_separate_etcd')
		# To test different cookbook versions
		shutit.get_config(self.module_id,'chef_yum_cookbook_version',default='latest')
		shutit.get_config(self.module_id,'chef_iptables_cookbook_version',default='latest')
		shutit.get_config(self.module_id,'chef_docker_cookbook_version',default='latest')
		shutit.get_config(self.module_id,'chef_selinux_policy_cookbook_version',default='latest')
		shutit.get_config(self.module_id,'chef_compat_resource_cookbook_version',default='latest')
		shutit.get_config(self.module_id,'pw',default='')
		shutit.get_config(self.module_id,'ose_major_version',default='3.7')
		shutit.get_config(self.module_id,'cookbook_branch',default='master')
		shutit.get_config(self.module_id,'ose_version',default='3.7')
		shutit.get_config(self.module_id,'inject_compat_resource',default=False,boolean=True)
		shutit.get_config(self.module_id,'cluster_vm_names',default='shutit_openshift_cluster')
		# Check all is OK/Sane
		shutit.get_config(self.module_id,'chef_deploy_method',default='solo')
		assert shutit.cfg[self.module_id]['chef_deploy_method'] in ('solo','server')
		for upgrade_item in ('do_upgrade_14_15','do_upgrade_15_36','do_upgrade_36_37','do_upgrade_37_39'):
			shutit.get_config(self.module_id,upgrade_item)
			if shutit.cfg[self.module_id][upgrade_item] == 'true':
				shutit.cfg[self.module_id][upgrade_item] = True
			else:
				shutit.cfg[self.module_id][upgrade_item] = False
		# chef_deploy_containerized
		shutit.get_config(self.module_id,'chef_deploy_containerized',default='true')
		assert shutit.cfg[self.module_id]['chef_deploy_containerized'] in ('true','false')
		if shutit.cfg[self.module_id]['chef_deploy_containerized'] == 'true':
			shutit.cfg[self.module_id]['chef_deploy_containerized'] = True
			shutit.get_config(self.module_id,'openshift_docker_image_version')
		else:
			shutit.cfg[self.module_id]['chef_deploy_containerized'] = False
			shutit.get_config(self.module_id,'openshift_docker_image_version',default=None)
		# do adhoc uninstall
		shutit.get_config(self.module_id,'do_adhoc_uninstall',default='false')
		assert shutit.cfg[self.module_id]['do_adhoc_uninstall'] in ('true','false')
		if shutit.cfg[self.module_id]['do_adhoc_uninstall'] == 'true':
			shutit.cfg[self.module_id]['do_adhoc_uninstall'] = True
		else:
			shutit.cfg[self.module_id]['do_adhoc_uninstall'] = False
		# do adhoc reset
		shutit.get_config(self.module_id,'do_adhoc_reset',default='false')
		assert shutit.cfg[self.module_id]['do_adhoc_reset'] in ('true','false')
		if shutit.cfg[self.module_id]['do_adhoc_reset'] == 'true':
			shutit.cfg[self.module_id]['do_adhoc_reset'] = True
		else:
			shutit.cfg[self.module_id]['do_adhoc_reset'] = False
		# Istio
		shutit.get_config(self.module_id,'do_istio',default=False,boolean=True)
		# Vault
		shutit.get_config(self.module_id,'do_vault',default=False,boolean=True)
		# Cluster CRD
		shutit.get_config(self.module_id,'do_crd',default=False,boolean=True)
		return True


def module():
	return shutit_openshift_cluster(
		'tk.shutit.shutit_openshift_cluster.shutit_openshift_cluster', 857091783.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)
