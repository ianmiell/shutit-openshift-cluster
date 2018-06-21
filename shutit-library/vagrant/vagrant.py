"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class vagrant(ShutItModule):


	def build(self, shutit):
		cfg=shutit.cfg
		vagrant_version = '1.8.6'
		processor = shutit.send_and_get_output('uname -p')
		if not shutit.command_available('wget'):
			shutit.install('wget')
		if not shutit.command_available('vagrant'):
			if shutit.get_current_shutit_pexpect_session_environment().install_type == 'apt':
				pw = shutit.get_env_pass('Input your sudo password to install vagrant')
				shutit.send('wget -qO- https://releases.hashicorp.com/vagrant/' + vagrant_version + '/vagrant_' + vagrant_version + '_' + processor + '.deb > /tmp/vagrant.deb',note='Downloading vagrant and installing')
				shutit.multisend('sudo dpkg -i /tmp/vagrant.deb',{'assword':pw})
				shutit.send('rm -f /tmp/vagrant.deb')
			elif shutit.get_current_shutit_pexpect_session_environment().install_type == 'yum':
				pw = shutit.get_env_pass('Input your sudo password to install vagrant')
				shutit.send('wget -qO- https://releases.hashicorp.com/vagrant/' + vagrant_version + '/vagrant_' + vagrant_version + '_' + processor + '.rpm > /tmp/vagrant.rpm',note='Downloading vagrant and installing')
				shutit.multisend('sudo rpm -i /tmp/vagrant.rpm',{'assword':pw})
				shutit.send('rm -f /tmp/vagrant.rpm')
			else:
				shutit.install('vagrant')
		# do not move this!
		# Need the try in case the virtualization item is not set
		try:
			if shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] == 'libvirt' and shutit.send_and_get_output('vagrant plugin list | grep vagrant-libvirt') == '':
					if shutit.get_current_shutit_pexpect_session_environment().install_type == 'yum':
						shutit.install('gcc-c++')
					shutit.install('gcc')
					shutit.install('libvirt')
					shutit.install('libvirt-devel')
					shutit.install('qemu-kvm')
					pw = shutit.get_env_pass()
					shutit.multisend('sudo /opt/vagrant/embedded/bin/gem source -r https://rubygems.org/',{'assword':pw})
					shutit.multisend('sudo /opt/vagrant/embedded/bin/gem source -a http://rubygems.org/', {'Do you want to add this insecure source?':'y','assword':pw})
					shutit.multisend('sudo /opt/vagrant/embedded/bin/gem update --system --no-doc',{'assword':pw})
					shutit.multisend('sudo /opt/vagrant/embedded/bin/gem source -r http://rubygems.org/',{'assword':pw})
					shutit.multisend('sudo /opt/vagrant/embedded/bin/gem source -a https://rubygems.org/',{'assword':pw})
					shutit.multisend('sudo vagrant plugin install vagrant-libvirt',{'assword':pw})
					# https://github.com/vagrant-libvirt/vagrant-libvirt/issues/568
					if shutit.send_and_get_output('vagrant plugin list | grep fog | grep 0.0.4 | wc -l') == '1':
						shutit.multisend('sudo /opt/vagrant/embedded/bin/gem uninstall -i ~/.vagrant.d/gems --version 0.0.4 fog-libvirt',{'assword':pwd})
						shutit.multisend('vagrant plugin install fog-libvirt --plugin-version 0.0.3',{'assword':pwd})
			if shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] == 'libvirt':
				pw = shutit.get_env_pass()
				shutit.multisend('sudo systemctl start libvirtd',{'assword':pw})
			else:
				if shutit.send_and_get_output("""vagrant version  | head -1 | awk '{print $3}'""") < '1.8.6':
					shutit.log('Vagrant version may be too low!')
					shutit.send('echo VAGRANT VERSION MAY BE TOO LOW SEE https://github.com/ianmiell/shutit-library/issues/1 && sleep 10')
		except:
			pass
		return True

	def get_config(self, shutit):
		# CONFIGURATION
		# shutit.get_config(module_id,option,default=None,boolean=False)
		#                                    - Get configuration value, boolean indicates whether the item is
		#                                      a boolean type, eg get the config with:
		# shutit.get_config(self.module_id, 'myconfig', default='a value')
		#                                      and reference in your code with:
		# shutit.cfg[self.module_id]['myconfig']
		return True

	def test(self, shutit):
		# For test cycle part of the ShutIt build.
		return True

	def finalize(self, shutit):
		# Any cleanup required at the end.
		return True
	
	def is_installed(self, shutit):
		return False


	#Class-level functions
	def restore(shutit):
		if shutit.send_and_match_output('vagrant status',['.*running.*','.*saved.*','.*poweroff.*','.*not created.*','.*aborted.*']):
			if not shutit.send_and_match_output('vagrant status',['.*running.*','.*not created.*']) and shutit.get_input('A vagrant setup already exists here. Do you want me to start up the existing instance (y) or destroy it (n)?',boolean=True):
				shutit.send('vagrant up')
				return True
			elif not shutit.send_and_match_output('vagrant status',['.*not created.*']):
				shutit.send('vagrant up')
				return True
			elif not shutit.send_and_match_output('vagrant status',['.*running.*']):
				shutit.send('vagrant destroy -f')
				shutit.send('vagrant up')
				return True
			else:
				return False
		else:
			return False


def module():
	return vagrant(
		'tk.shutit.vagrant.vagrant.vagrant', 0.941247152,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit-library.virtualization.virtualization.virtualization']
	)

